import Database from 'better-sqlite3';
import { initDatabase } from './migrate.js';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const DB_PATH = process.env.DATABASE_PATH || path.resolve(__dirname, '../../../../data/database.sqlite');

let db: Database.Database | null = null;

export function getDb(): Database.Database {
  if (!db) {
    db = initDatabase(DB_PATH);
  }
  return db;
}

// Competitors
export function addCompetitor(name: string, xUrl: string, handle?: string) {
  const stmt = getDb().prepare('INSERT OR IGNORE INTO competitors (name, x_url, handle) VALUES (?, ?, ?)');
  return stmt.run(name, xUrl, handle || xUrl.split('/').pop() || '');
}

export function getCompetitors() {
  return getDb().prepare('SELECT * FROM competitors ORDER BY created_at DESC').all();
}

export function getCompetitorByName(name: string) {
  return getDb().prepare('SELECT * FROM competitors WHERE name = ?').get(name) as any;
}

// Crawl Jobs
export function createCrawlJob(competitorId: number | null, targetUrl: string, targetType: string, opts: { maxPosts?: number; maxReplies?: number; crawlPasses?: number } = {}) {
  const stmt = getDb().prepare("INSERT INTO crawl_jobs (competitor_id, target_url, target_type, status, started_at, max_posts, max_replies, crawl_passes) VALUES (?, ?, ?, ?, datetime('now'), ?, ?, ?)");
  return stmt.run(competitorId, targetUrl, targetType, 'running', opts.maxPosts || null, opts.maxReplies || null, opts.crawlPasses || 1);
}

export function updateCrawlJob(id: number, updates: { status?: string; completenessScore?: number; errorMessage?: string }) {
  const parts: string[] = [];
  const values: any[] = [];
  if (updates.status) { parts.push('status = ?'); values.push(updates.status); }
  if (updates.completenessScore !== undefined) { parts.push('completeness_score = ?'); values.push(updates.completenessScore); }
  if (updates.errorMessage !== undefined) { parts.push('error_message = ?'); values.push(updates.errorMessage); }
  parts.push("finished_at = datetime('now')");
  values.push(id);
  getDb().prepare(`UPDATE crawl_jobs SET ${parts.join(', ')} WHERE id = ?`).run(...values);
}

// Posts
export function upsertPost(data: { competitorId?: number; postId: string; url?: string; authorName?: string; authorHandle?: string; content?: string; language?: string; postedAt?: string; isRepost?: boolean; isQuote?: boolean; isReply?: boolean; hashtags?: string[]; mentions?: string[]; externalLinks?: string[] }) {
  const stmt = getDb().prepare(`INSERT INTO posts (competitor_id, post_id, url, author_name, author_handle, content, language, posted_at, is_repost, is_quote, is_reply, hashtags, mentions, external_links) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) ON CONFLICT(post_id) DO UPDATE SET content=excluded.content, updated_at=datetime('now')`);
  return stmt.run(
    data.competitorId || null, data.postId, data.url || null, data.authorName || null,
    data.authorHandle || null, data.content || null, data.language || null, data.postedAt || null,
    data.isRepost ? 1 : 0, data.isQuote ? 1 : 0, data.isReply ? 1 : 0,
    JSON.stringify(data.hashtags || []), JSON.stringify(data.mentions || []), JSON.stringify(data.externalLinks || [])
  );
}

export function getPostByPostId(postId: string) {
  return getDb().prepare('SELECT * FROM posts WHERE post_id = ?').get(postId) as any;
}

export function getPostsByCompetitor(competitorId: number, limit = 100) {
  return getDb().prepare('SELECT * FROM posts WHERE competitor_id = ? ORDER BY posted_at DESC LIMIT ?').all(competitorId, limit);
}

// Post Metrics
export function insertMetricsSnapshot(postDbId: number, metrics: { likeCount: number; replyCount: number; repostCount: number; quoteCount: number; viewCount: number }) {
  const stmt = getDb().prepare('INSERT INTO post_metrics_snapshots (post_id, like_count, reply_count, repost_count, quote_count, view_count) VALUES (?, ?, ?, ?, ?, ?)');
  return stmt.run(postDbId, metrics.likeCount, metrics.replyCount, metrics.repostCount, metrics.quoteCount, metrics.viewCount);
}

// Post Media
export function insertPostMedia(postDbId: number, media: { mediaType: string; mediaUrl: string; localPath?: string; altText?: string; hash?: string }) {
  const existing = getDb().prepare('SELECT id FROM post_media WHERE post_id = ? AND media_url = ?').get(postDbId, media.mediaUrl);
  if (existing) return;
  const stmt = getDb().prepare("INSERT INTO post_media (post_id, media_type, media_url, local_path, alt_text, hash, downloaded_at) VALUES (?, ?, ?, ?, ?, ?, datetime('now'))");
  return stmt.run(postDbId, media.mediaType, media.mediaUrl, media.localPath || null, media.altText || null, media.hash || null);
}

// Replies
export function upsertReply(data: { postDbId: number; replyId: string; parentReplyId?: string; url?: string; authorName?: string; authorHandle?: string; content?: string; language?: string; likeCount?: number; repostCount?: number; repliedAt?: string; isNested?: boolean }) {
  const stmt = getDb().prepare(`INSERT INTO replies (post_id, reply_id, parent_reply_id, url, author_name, author_handle, content, language, like_count, repost_count, replied_at, is_nested) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) ON CONFLICT(reply_id) DO UPDATE SET content=excluded.content, like_count=excluded.like_count, repost_count=excluded.repost_count, updated_at=datetime('now')`);
  return stmt.run(
    data.postDbId, data.replyId, data.parentReplyId || null, data.url || null,
    data.authorName || null, data.authorHandle || null, data.content || null,
    data.language || null, data.likeCount || 0, data.repostCount || 0,
    data.repliedAt || null, data.isNested ? 1 : 0
  );
}

export function getRepliesByPost(postDbId: number) {
  return getDb().prepare('SELECT * FROM replies WHERE post_id = ? ORDER BY replied_at ASC').all(postDbId);
}

export function getReplyCount(postDbId: number): number {
  const row = getDb().prepare('SELECT COUNT(*) as cnt FROM replies WHERE post_id = ?').get(postDbId) as any;
  return row?.cnt || 0;
}

// Crawl Logs
export function insertCrawlLog(jobId: number | null, level: string, message: string, context?: any) {
  const stmt = getDb().prepare('INSERT INTO crawl_logs (job_id, level, message, context_json) VALUES (?, ?, ?, ?)');
  return stmt.run(jobId, level, message, context ? JSON.stringify(context) : null);
}

// Analysis
export function insertAnalysisReport(data: { competitorId?: number; jobId?: number; title: string; dateRangeStart?: string; dateRangeEnd?: string; summaryJson?: string; markdownPath?: string }) {
  const stmt = getDb().prepare('INSERT INTO analysis_reports (competitor_id, job_id, title, date_range_start, date_range_end, summary_json, markdown_path) VALUES (?, ?, ?, ?, ?, ?, ?)');
  return stmt.run(data.competitorId || null, data.jobId || null, data.title, data.dateRangeStart || null, data.dateRangeEnd || null, data.summaryJson || null, data.markdownPath || null);
}

export function getAllPosts(limit = 200) {
  return getDb().prepare('SELECT * FROM posts ORDER BY posted_at DESC LIMIT ?').all(limit);
}

export function getAllRepliesWithPosts(competitorId?: number) {
  let sql = `SELECT r.*, p.post_id as parent_post_id, p.url as post_url, p.author_handle as post_author FROM replies r JOIN posts p ON r.post_id = p.id`;
  if (competitorId) sql += ` WHERE p.competitor_id = ?`;
  sql += ` ORDER BY r.replied_at DESC`;
  return competitorId ? getDb().prepare(sql).all(competitorId) : getDb().prepare(sql).all();
}
