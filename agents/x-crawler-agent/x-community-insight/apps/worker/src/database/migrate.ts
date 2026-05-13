import Database from 'better-sqlite3';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const DB_PATH = process.env.DATABASE_PATH || path.resolve(__dirname, '../../../../data/database.sqlite');

const SCHEMA = `
CREATE TABLE IF NOT EXISTS competitors (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  x_url TEXT NOT NULL UNIQUE,
  handle TEXT,
  created_at TEXT DEFAULT (datetime('now')),
  updated_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS crawl_jobs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  competitor_id INTEGER,
  target_url TEXT NOT NULL,
  target_type TEXT NOT NULL CHECK(target_type IN ('account', 'post')),
  status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending', 'running', 'completed', 'failed', 'cancelled')),
  started_at TEXT,
  finished_at TEXT,
  max_posts INTEGER,
  max_replies INTEGER,
  crawl_passes INTEGER DEFAULT 1,
  completeness_score REAL,
  error_message TEXT,
  FOREIGN KEY (competitor_id) REFERENCES competitors(id)
);

CREATE TABLE IF NOT EXISTS posts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  competitor_id INTEGER,
  post_id TEXT NOT NULL UNIQUE,
  url TEXT,
  author_name TEXT,
  author_handle TEXT,
  content TEXT,
  language TEXT,
  posted_at TEXT,
  is_repost INTEGER DEFAULT 0,
  is_quote INTEGER DEFAULT 0,
  is_reply INTEGER DEFAULT 0,
  hashtags TEXT,
  mentions TEXT,
  external_links TEXT,
  raw_json TEXT,
  created_at TEXT DEFAULT (datetime('now')),
  updated_at TEXT DEFAULT (datetime('now')),
  FOREIGN KEY (competitor_id) REFERENCES competitors(id)
);

CREATE TABLE IF NOT EXISTS post_metrics_snapshots (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  post_id INTEGER NOT NULL,
  like_count INTEGER DEFAULT 0,
  reply_count INTEGER DEFAULT 0,
  repost_count INTEGER DEFAULT 0,
  quote_count INTEGER DEFAULT 0,
  view_count INTEGER DEFAULT 0,
  captured_at TEXT DEFAULT (datetime('now')),
  FOREIGN KEY (post_id) REFERENCES posts(id)
);

CREATE TABLE IF NOT EXISTS post_media (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  post_id INTEGER NOT NULL,
  media_type TEXT CHECK(media_type IN ('image', 'video', 'gif')),
  media_url TEXT NOT NULL,
  local_path TEXT,
  alt_text TEXT,
  hash TEXT,
  downloaded_at TEXT,
  FOREIGN KEY (post_id) REFERENCES posts(id)
);

CREATE TABLE IF NOT EXISTS replies (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  post_id INTEGER NOT NULL,
  reply_id TEXT NOT NULL,
  parent_reply_id TEXT,
  url TEXT,
  author_name TEXT,
  author_handle TEXT,
  content TEXT,
  language TEXT,
  like_count INTEGER DEFAULT 0,
  repost_count INTEGER DEFAULT 0,
  replied_at TEXT,
  is_nested INTEGER DEFAULT 0,
  raw_json TEXT,
  created_at TEXT DEFAULT (datetime('now')),
  updated_at TEXT DEFAULT (datetime('now')),
  FOREIGN KEY (post_id) REFERENCES posts(id),
  UNIQUE(reply_id)
);

CREATE TABLE IF NOT EXISTS reply_media (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  reply_id INTEGER NOT NULL,
  media_type TEXT CHECK(media_type IN ('image', 'video', 'gif')),
  media_url TEXT NOT NULL,
  local_path TEXT,
  alt_text TEXT,
  hash TEXT,
  downloaded_at TEXT,
  FOREIGN KEY (reply_id) REFERENCES replies(id)
);

CREATE TABLE IF NOT EXISTS feedback_categories (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL UNIQUE,
  description TEXT,
  keywords_json TEXT,
  severity_weight REAL DEFAULT 1.0
);

CREATE TABLE IF NOT EXISTS analysis_reports (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  competitor_id INTEGER,
  job_id INTEGER,
  title TEXT,
  date_range_start TEXT,
  date_range_end TEXT,
  summary_json TEXT,
  markdown_path TEXT,
  html_path TEXT,
  csv_path TEXT,
  json_path TEXT,
  created_at TEXT DEFAULT (datetime('now')),
  FOREIGN KEY (competitor_id) REFERENCES competitors(id),
  FOREIGN KEY (job_id) REFERENCES crawl_jobs(id)
);

CREATE TABLE IF NOT EXISTS crawl_logs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  job_id INTEGER,
  level TEXT NOT NULL CHECK(level IN ('info', 'warn', 'error', 'debug')),
  message TEXT NOT NULL,
  context_json TEXT,
  created_at TEXT DEFAULT (datetime('now')),
  FOREIGN KEY (job_id) REFERENCES crawl_jobs(id)
);

CREATE INDEX IF NOT EXISTS idx_posts_competitor ON posts(competitor_id);
CREATE INDEX IF NOT EXISTS idx_posts_post_id ON posts(post_id);
CREATE INDEX IF NOT EXISTS idx_replies_post_id ON replies(post_id);
CREATE INDEX IF NOT EXISTS idx_replies_reply_id ON replies(reply_id);
CREATE INDEX IF NOT EXISTS idx_crawl_logs_job ON crawl_logs(job_id);
CREATE INDEX IF NOT EXISTS idx_post_metrics_post ON post_metrics_snapshots(post_id);
`;

export function initDatabase(dbPath?: string): Database.Database {
  const db = new Database(dbPath || DB_PATH);
  db.pragma('journal_mode = WAL');
  db.pragma('foreign_keys = ON');
  db.exec(SCHEMA);
  return db;
}

// Run migration if executed directly
if (process.argv[1]?.includes('migrate')) {
  const db = initDatabase();
  console.log('✅ 資料庫初始化完成:', DB_PATH);
  db.close();
}
