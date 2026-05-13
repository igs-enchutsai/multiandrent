import fs from 'fs';
import path from 'path';
import crypto from 'crypto';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const MEDIA_DIR = path.resolve(__dirname, '../../../../data/media');

// 確保目錄存在
if (!fs.existsSync(MEDIA_DIR)) {
  fs.mkdirSync(MEDIA_DIR, { recursive: true });
}

/**
 * 下載媒體檔案到本地，支援去重（hash 比對）
 */
export async function downloadMedia(url: string, postId: string): Promise<string | null> {
  try {
    if (!url || url.startsWith('data:')) return null;

    // 產生檔名
    const urlHash = crypto.createHash('md5').update(url).digest('hex').slice(0, 8);
    const ext = getExtFromUrl(url);
    const filename = `${postId}_${urlHash}${ext}`;
    const localPath = path.join(MEDIA_DIR, filename);

    // 已存在則跳過
    if (fs.existsSync(localPath)) {
      return localPath;
    }

    // 下載
    const response = await fetch(url);
    if (!response.ok) return null;

    const buffer = Buffer.from(await response.arrayBuffer());

    // 用內容 hash 檢查是否已有相同檔案
    const contentHash = crypto.createHash('md5').update(buffer).digest('hex');
    const existingByHash = findByHash(contentHash);
    if (existingByHash) return existingByHash;

    fs.writeFileSync(localPath, buffer);
    return localPath;
  } catch {
    return null;
  }
}

/**
 * 計算檔案 hash
 */
export function getFileHash(filePath: string): string {
  const buffer = fs.readFileSync(filePath);
  return crypto.createHash('md5').update(buffer).digest('hex');
}

function getExtFromUrl(url: string): string {
  const match = url.match(/\.(jpg|jpeg|png|gif|webp|mp4)/i);
  return match ? `.${match[1].toLowerCase()}` : '.jpg';
}

function findByHash(hash: string): string | null {
  // 簡單實作：掃描 media 目錄比對（小規模可用）
  const files = fs.readdirSync(MEDIA_DIR);
  for (const file of files.slice(-100)) { // 只檢查最近 100 個
    const filePath = path.join(MEDIA_DIR, file);
    try {
      const fileHash = crypto.createHash('md5').update(fs.readFileSync(filePath)).digest('hex');
      if (fileHash === hash) return filePath;
    } catch { continue; }
  }
  return null;
}
