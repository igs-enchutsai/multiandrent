import { Page } from 'playwright';
import { safeWait, normalizeCountText, extractHashtags, extractMentions, detectLanguage } from '../utils/helpers.js';
import { upsertPost, getPostByPostId, insertMetricsSnapshot, insertCrawlLog } from '../database/repository.js';

export interface CrawlAccountOptions {
  url: string;
  maxPosts?: number;
  days?: number;
  maxEmptyRounds?: number;
  jobId?: number;
  competitorId?: number;
}

/**
 * 爬取帳號頁面，蒐集貼文列表
 */
export async function crawlAccount(page: Page, options: CrawlAccountOptions): Promise<{ postsCollected: number }> {
  const { url, maxPosts = 100, days, maxEmptyRounds = 3, jobId, competitorId } = options;

  const cutoffDate = days ? new Date(Date.now() - days * 86400000) : null;

  log(jobId, 'info', `開始爬取帳號: ${url}, 最多 ${maxPosts} 篇, ${days ? `近 ${days} 天` : '不限時間'}`);

  await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
  await safeWait(3000, 5000);

  // 等待貼文載入
  try {
    await page.waitForSelector('article[data-testid="tweet"]', { timeout: 15000 });
  } catch {
    log(jobId, 'error', '頁面未載入貼文，可能需要登入或帳號不存在');
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
        // 取得貼文連結以提取 post_id
        const statusLink = await article.$eval('a[href*="/status/"]', el => el.getAttribute('href') || '').catch(() => '');
        const postIdMatch = statusLink.match(/status\/(\d+)/);
        if (!postIdMatch) continue;

        const postId = postIdMatch[1];
        if (seenPostIds.has(postId)) continue;
        seenPostIds.add(postId);

        // 發文時間
        const timeEl = await article.$('time');
        const postedAt = timeEl ? (await timeEl.getAttribute('datetime') || '') : '';

        // 時間範圍過濾
        if (cutoffDate && postedAt) {
          const postDate = new Date(postedAt);
          if (postDate < cutoffDate) {
            log(jobId, 'info', `貼文超出時間範圍，停止蒐集`);
            return { postsCollected: totalCollected };
          }
        }

        // 作者
        const authorName = await article.$eval('[data-testid="User-Name"] span', el => el.textContent || '').catch(() => '');
        const authorHandle = await article.$eval('a[role="link"][href*="/"]', el => {
          const href = el.getAttribute('href') || '';
          return href.split('/')[1] || '';
        }).catch(() => '');

        // 內容
        const content = await article.$eval('[data-testid="tweetText"]', el => el.textContent || '').catch(() => '');

        // 互動數據
        const replyCount = normalizeCountText(await article.$eval('[data-testid="reply"] span', el => el.textContent).catch(() => '0'));
        const repostCount = normalizeCountText(await article.$eval('[data-testid="retweet"] span', el => el.textContent).catch(() => '0'));
        const likeCount = normalizeCountText(await article.$eval('[data-testid="like"] span', el => el.textContent).catch(() => '0'));
        const viewCount = normalizeCountText(await article.$eval('a[href*="/analytics"] span', el => el.textContent).catch(() => '0'));

        // 判斷類型
        const isRepost = !!(await article.$('[data-testid="socialContext"]').catch(() => null));

        // 儲存
        upsertPost({
          competitorId,
          postId,
          url: `https://x.com${statusLink}`,
          authorName,
          authorHandle,
          content,
          language: detectLanguage(content),
          postedAt,
          isRepost,
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

    // 滾動
    await page.evaluate(() => window.scrollBy(0, 1000));
    await safeWait(2000, 5000);
  }

  log(jobId, 'info', `帳號爬取完成: 共蒐集 ${totalCollected} 篇貼文`);
  return { postsCollected: totalCollected };
}

function log(jobId: number | undefined, level: string, message: string) {
  console.log(`[${level.toUpperCase()}] ${message}`);
  if (jobId) {
    try { insertCrawlLog(jobId, level, message); } catch { /* ignore */ }
  }
}
