import { Page } from 'playwright';
import { safeWait, normalizeCountText, extractHashtags, extractMentions, detectLanguage } from '../utils/helpers.js';
import { upsertPost, getPostByPostId, insertMetricsSnapshot, insertCrawlLog } from '../database/repository.js';

export interface CrawlHashtagOptions {
  hashtag: string;
  maxPosts?: number;
  maxEmptyRounds?: number;
  jobId?: number;
  competitorId?: number;
}

/**
 * 爬取 X 搜尋頁面，以 hashtag 為關鍵字蒐集貼文
 */
export async function crawlHashtag(page: Page, options: CrawlHashtagOptions): Promise<{ postsCollected: number }> {
  const { hashtag, maxPosts = 30, maxEmptyRounds = 3, jobId, competitorId } = options;

  // 構建搜尋 URL（使用 Latest tab 取得最新貼文）
  const tag = hashtag.startsWith('#') ? hashtag.slice(1) : hashtag;
  const searchUrl = `https://x.com/search?q=%23${encodeURIComponent(tag)}&src=typed_query&f=live`;

  log(jobId, 'info', `開始搜尋 hashtag: #${tag}, 最多 ${maxPosts} 篇`);

  await page.goto(searchUrl, { waitUntil: 'domcontentloaded', timeout: 30000 });
  await safeWait(4000, 6000);

  // 等待貼文載入
  try {
    await page.waitForSelector('article[data-testid="tweet"]', { timeout: 20000 });
  } catch {
    log(jobId, 'error', '搜尋頁面未載入貼文，可能需要登入或無搜尋結果');
    return { postsCollected: 0 };
  }

  let totalCollected = 0;
  let emptyRounds = 0;
  let round = 0;
  const seenPostIds = new Set<string>();

  while (totalCollected < maxPosts && emptyRounds < maxEmptyRounds) {
    round++;
    let newInRound = 0;

    const articles = await page.$$('article[data-testid="tweet"]');

    for (const article of articles) {
      if (totalCollected >= maxPosts) break;

      try {
        const statusLink = await article.$eval('a[href*="/status/"]', el => el.getAttribute('href') || '').catch(() => '');
        const postIdMatch = statusLink.match(/status\/(\d+)/);
        if (!postIdMatch) continue;

        const postId = postIdMatch[1];
        if (seenPostIds.has(postId)) continue;
        seenPostIds.add(postId);

        const timeEl = await article.$('time');
        const postedAt = timeEl ? (await timeEl.getAttribute('datetime') || '') : '';

        const authorName = await article.$eval('[data-testid="User-Name"] span', el => el.textContent || '').catch(() => '');
        const authorHandle = await article.$eval('a[role="link"][href*="/"]', el => {
          const href = el.getAttribute('href') || '';
          return href.split('/')[1] || '';
        }).catch(() => '');

        const content = await article.$eval('[data-testid="tweetText"]', el => el.textContent || '').catch(() => '');

        const replyCount = normalizeCountText(await article.$eval('[data-testid="reply"] span', el => el.textContent).catch(() => '0'));
        const repostCount = normalizeCountText(await article.$eval('[data-testid="retweet"] span', el => el.textContent).catch(() => '0'));
        const likeCount = normalizeCountText(await article.$eval('[data-testid="like"] span', el => el.textContent).catch(() => '0'));
        const viewCount = normalizeCountText(await article.$eval('a[href*="/analytics"] span', el => el.textContent).catch(() => '0'));

        upsertPost({
          competitorId,
          postId,
          url: `https://x.com${statusLink}`,
          authorName,
          authorHandle,
          content,
          language: detectLanguage(content),
          postedAt,
          isRepost: false,
          isQuote: false,
          isReply: false,
          hashtags: extractHashtags(content),
          mentions: extractMentions(content),
        });

        const postRow = getPostByPostId(postId);
        if (postRow) {
          insertMetricsSnapshot(postRow.id, { likeCount, replyCount, repostCount, quoteCount: 0, viewCount });
        }

        newInRound++;
        totalCollected++;
        log(jobId, 'debug', `[${totalCollected}/${maxPosts}] @${authorHandle}: ${content.slice(0, 50)}...`);
      } catch {
        continue;
      }
    }

    if (newInRound === 0) {
      emptyRounds++;
    } else {
      emptyRounds = 0;
    }

    log(jobId, 'debug', `滾動第 ${round} 輪: 新增 ${newInRound} 篇, 累計 ${totalCollected} 篇`);

    // 滾動頁面
    await page.evaluate(() => window.scrollBy(0, 1000));
    await safeWait(2500, 5000);
  }

  log(jobId, 'info', `Hashtag 搜尋完成: 共蒐集 ${totalCollected} 篇貼文`);
  return { postsCollected: totalCollected };
}

function log(jobId: number | undefined, level: string, message: string) {
  console.log(`[${level.toUpperCase()}] ${message}`);
  if (jobId) {
    try { insertCrawlLog(jobId, level, message); } catch { /* ignore */ }
  }
}
