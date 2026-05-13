import { Page } from 'playwright';
import { safeWait, normalizeCountText, extractHashtags, extractMentions, extractLinks, detectLanguage, calculateCompletenessScore } from '../utils/helpers.js';
import { upsertPost, getPostByPostId, insertMetricsSnapshot, upsertReply, getReplyCount, insertCrawlLog, insertPostMedia } from '../database/repository.js';
import { downloadMedia } from './media-downloader.js';

export interface CrawlPostOptions {
  url: string;
  maxReplies?: number;
  crawlPasses?: number;
  maxEmptyRounds?: number;
  jobId?: number;
  competitorId?: number;
}

export interface PostData {
  postId: string;
  url: string;
  authorName: string;
  authorHandle: string;
  content: string;
  postedAt: string;
  isRepost: boolean;
  isQuote: boolean;
  isReply: boolean;
  likeCount: number;
  replyCount: number;
  repostCount: number;
  quoteCount: number;
  viewCount: number;
  mediaUrls: string[];
}

/**
 * 爬取指定貼文頁面，蒐集主貼文 + 留言
 */
export async function crawlPost(page: Page, options: CrawlPostOptions): Promise<{ postDbId: number; repliesCollected: number; completenessScore: number }> {
  const { url, maxReplies = 500, crawlPasses = 3, maxEmptyRounds = 3, jobId, competitorId } = options;

  log(jobId, 'info', `開始爬取貼文: ${url}`);

  await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
  await safeWait(3000, 5000);

  // 擷取主貼文
  const postData = await extractMainPost(page, url);
  if (!postData) {
    log(jobId, 'error', '無法擷取主貼文內容');
    return { postDbId: 0, repliesCollected: 0, completenessScore: 0 };
  }

  // 儲存主貼文
  const result = upsertPost({
    competitorId,
    postId: postData.postId,
    url: postData.url,
    authorName: postData.authorName,
    authorHandle: postData.authorHandle,
    content: postData.content,
    language: detectLanguage(postData.content),
    postedAt: postData.postedAt,
    isRepost: postData.isRepost,
    isQuote: postData.isQuote,
    isReply: postData.isReply,
    hashtags: extractHashtags(postData.content),
    mentions: extractMentions(postData.content),
    externalLinks: extractLinks(postData.content),
  });

  const postRow = getPostByPostId(postData.postId);
  const postDbId = postRow?.id;
  if (!postDbId) {
    log(jobId, 'error', '無法取得貼文資料庫 ID');
    return { postDbId: 0, repliesCollected: 0, completenessScore: 0 };
  }

  // 儲存互動數據快照
  insertMetricsSnapshot(postDbId, {
    likeCount: postData.likeCount,
    replyCount: postData.replyCount,
    repostCount: postData.repostCount,
    quoteCount: postData.quoteCount,
    viewCount: postData.viewCount,
  });

  // 下載圖片
  for (const mediaUrl of postData.mediaUrls) {
    const localPath = await downloadMedia(mediaUrl, postData.postId);
    insertPostMedia(postDbId, { mediaType: 'image', mediaUrl, localPath });
  }

  log(jobId, 'info', `主貼文已儲存，開始蒐集留言 (最多 ${crawlPasses} 輪)`);

  // 多輪蒐集留言
  let totalNewReplies = 0;
  for (let pass = 0; pass < crawlPasses; pass++) {
    const newInPass = await collectReplies(page, postDbId, maxReplies, maxEmptyRounds, jobId);
    totalNewReplies += newInPass;
    log(jobId, 'info', `第 ${pass + 1} 輪完成，新增 ${newInPass} 則留言`);

    if (newInPass === 0 && pass > 0) {
      log(jobId, 'info', '連續輪次無新增留言，停止蒐集');
      break;
    }

    if (pass < crawlPasses - 1) {
      // 重新載入頁面進行下一輪
      await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
      await safeWait(3000, 5000);
    }
  }

  const actualCount = getReplyCount(postDbId);
  const displayedCount = postData.replyCount;
  const completenessScore = calculateCompletenessScore(displayedCount, actualCount);

  log(jobId, 'info', `爬取完成: 顯示留言數 ${displayedCount}, 實際蒐集 ${actualCount}, 完整度 ${completenessScore}%`);

  return { postDbId, repliesCollected: actualCount, completenessScore };
}

/**
 * 擷取主貼文資料
 */
async function extractMainPost(page: Page, url: string): Promise<PostData | null> {
  try {
    // 等待貼文內容載入
    await page.waitForSelector('article[data-testid="tweet"]', { timeout: 15000 });

    const article = await page.$('article[data-testid="tweet"]');
    if (!article) return null;

    // 提取貼文 ID from URL
    const postId = url.match(/status\/(\d+)/)?.[1] || '';

    // 作者資訊
    const authorName = await article.$eval('[data-testid="User-Name"] span', el => el.textContent || '').catch(() => '');
    const authorHandle = await article.$eval('[data-testid="User-Name"] a[href*="/"]', el => el.getAttribute('href')?.replace('/', '') || '').catch(() => '');

    // 貼文內容
    const content = await article.$eval('[data-testid="tweetText"]', el => el.textContent || '').catch(() => '');

    // 發文時間
    const timeEl = await article.$('time');
    const postedAt = timeEl ? (await timeEl.getAttribute('datetime') || '') : '';

    // 互動數據
    const metrics = await extractMetricsFromArticle(page, article);

    // 圖片
    const mediaUrls = await article.$$eval('[data-testid="tweetPhoto"] img', imgs => imgs.map(img => img.getAttribute('src') || '').filter(Boolean)).catch(() => []);

    return {
      postId,
      url,
      authorName,
      authorHandle,
      content,
      postedAt,
      isRepost: false,
      isQuote: false,
      isReply: false,
      ...metrics,
      mediaUrls,
    };
  } catch (err) {
    return null;
  }
}

/**
 * 從 article 元素提取互動數據
 */
async function extractMetricsFromArticle(page: Page, article: any): Promise<{ likeCount: number; replyCount: number; repostCount: number; quoteCount: number; viewCount: number }> {
  try {
    const replyCount = normalizeCountText(await article.$eval('[data-testid="reply"] span', el => el.textContent).catch(() => '0'));
    const repostCount = normalizeCountText(await article.$eval('[data-testid="retweet"] span', el => el.textContent).catch(() => '0'));
    const likeCount = normalizeCountText(await article.$eval('[data-testid="like"] span', el => el.textContent).catch(() => '0'));
    const viewCount = normalizeCountText(await article.$eval('a[href*="/analytics"] span', el => el.textContent).catch(() => '0'));

    return { likeCount, replyCount, repostCount, quoteCount: 0, viewCount };
  } catch {
    return { likeCount: 0, replyCount: 0, repostCount: 0, quoteCount: 0, viewCount: 0 };
  }
}

/**
 * 蒐集留言（滾動 + 擷取 + 去重）
 */
async function collectReplies(page: Page, postDbId: number, maxReplies: number, maxEmptyRounds: number, jobId?: number): Promise<number> {
  let totalNew = 0;
  let emptyRounds = 0;
  let round = 0;

  while (totalNew < maxReplies && emptyRounds < maxEmptyRounds) {
    round++;
    const newCount = await scrollAndExtractReplies(page, postDbId);

    if (newCount === 0) {
      emptyRounds++;
    } else {
      emptyRounds = 0;
      totalNew += newCount;
    }

    log(jobId, 'debug', `滾動第 ${round} 輪: 新增 ${newCount} 則, 累計新增 ${totalNew} 則`);

    // 滾動頁面
    await page.evaluate(() => window.scrollBy(0, 800));
    await safeWait(2000, 4000);
  }

  return totalNew;
}

/**
 * 滾動後擷取可見留言
 */
async function scrollAndExtractReplies(page: Page, postDbId: number): Promise<number> {
  let newCount = 0;

  const articles = await page.$$('article[data-testid="tweet"]');

  // 跳過第一個（主貼文），從第二個開始是留言
  for (let i = 1; i < articles.length; i++) {
    const article = articles[i];
    try {
      const authorHandle = await article.$eval('a[role="link"][href*="/"]', el => {
        const href = el.getAttribute('href') || '';
        return href.split('/')[1] || '';
      }).catch(() => '');

      const content = await article.$eval('[data-testid="tweetText"]', el => el.textContent || '').catch(() => '');
      if (!content) continue;

      const timeEl = await article.$('time');
      const repliedAt = timeEl ? (await timeEl.getAttribute('datetime') || '') : '';

      const authorName = await article.$eval('[data-testid="User-Name"] span', el => el.textContent || '').catch(() => '');

      const likeCount = normalizeCountText(await article.$eval('[data-testid="like"] span', el => el.textContent).catch(() => '0'));
      const repostCount = normalizeCountText(await article.$eval('[data-testid="retweet"] span', el => el.textContent).catch(() => '0'));

      // 用 author + time + content hash 作為 reply_id
      const replyId = `${authorHandle}_${repliedAt}_${hashString(content.slice(0, 50))}`;

      const statusLink = await article.$eval('a[href*="/status/"]', el => el.getAttribute('href') || '').catch(() => '');
      const replyUrl = statusLink ? `https://x.com${statusLink}` : '';

      const result = upsertReply({
        postDbId,
        replyId,
        url: replyUrl,
        authorName,
        authorHandle,
        content,
        language: detectLanguage(content),
        likeCount,
        repostCount,
        repliedAt,
        isNested: false,
      });

      if (result && result.changes > 0) newCount++;
    } catch {
      continue;
    }
  }

  return newCount;
}

function hashString(str: string): string {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash |= 0;
  }
  return Math.abs(hash).toString(36);
}

function log(jobId: number | undefined, level: string, message: string) {
  console.log(`[${level.toUpperCase()}] ${message}`);
  if (jobId) {
    try { insertCrawlLog(jobId, level, message); } catch { /* ignore */ }
  }
}
