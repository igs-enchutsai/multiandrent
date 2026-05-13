/**
 * 隨機等待，模擬人類行為
 */
export function safeWait(minMs = 3000, maxMs = 8000): Promise<void> {
  const ms = Math.floor(Math.random() * (maxMs - minMs)) + minMs;
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * 將 K/M/萬 等縮寫轉為數字
 * 1.2K -> 1200, 3M -> 3000000, 1萬 -> 10000, 2.5萬 -> 25000
 */
export function normalizeCountText(text: string | null | undefined): number {
  if (!text) return 0;
  const cleaned = text.trim().replace(/,/g, '');
  if (!cleaned || cleaned === '') return 0;

  // 萬
  const wanMatch = cleaned.match(/^([\d.]+)\s*萬$/);
  if (wanMatch) return Math.round(parseFloat(wanMatch[1]) * 10000);

  // K
  const kMatch = cleaned.match(/^([\d.]+)\s*[Kk]$/);
  if (kMatch) return Math.round(parseFloat(kMatch[1]) * 1000);

  // M
  const mMatch = cleaned.match(/^([\d.]+)\s*[Mm]$/);
  if (mMatch) return Math.round(parseFloat(mMatch[1]) * 1000000);

  // B
  const bMatch = cleaned.match(/^([\d.]+)\s*[Bb]$/);
  if (bMatch) return Math.round(parseFloat(bMatch[1]) * 1000000000);

  const num = parseInt(cleaned, 10);
  return isNaN(num) ? 0 : num;
}

/**
 * 用 ID 或內容 hash 去重
 */
export function dedupeByIdOrHash<T extends { id?: string; hash?: string }>(items: T[]): T[] {
  const seen = new Set<string>();
  return items.filter(item => {
    const key = item.id || item.hash || JSON.stringify(item);
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

/**
 * 計算資料完整性分數
 */
export function calculateCompletenessScore(displayedCount: number, actualCount: number): number {
  if (displayedCount <= 0) return 100;
  const ratio = (actualCount / displayedCount) * 100;
  return Math.min(100, Math.round(ratio));
}

/**
 * 帶指數退避的重試
 */
export async function retryWithBackoff<T>(fn: () => Promise<T>, maxRetries = 3): Promise<T> {
  const delays = [3000, 10000, 30000];
  for (let i = 0; i <= maxRetries; i++) {
    try {
      return await fn();
    } catch (err) {
      if (i === maxRetries) throw err;
      await new Promise(r => setTimeout(r, delays[i]));
    }
  }
  throw new Error('Unreachable');
}

/**
 * 從文字中提取 hashtags
 */
export function extractHashtags(text: string): string[] {
  const matches = text.match(/#[\w\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff]+/g);
  return matches || [];
}

/**
 * 從文字中提取 mentions
 */
export function extractMentions(text: string): string[] {
  const matches = text.match(/@[\w]+/g);
  return matches || [];
}

/**
 * 從文字中提取外部連結
 */
export function extractLinks(text: string): string[] {
  const matches = text.match(/https?:\/\/[^\s]+/g);
  return matches || [];
}

/**
 * 簡單語言偵測
 */
export function detectLanguage(text: string): string {
  if (/[\u4e00-\u9fff]/.test(text)) return 'zh';
  if (/[\u3040-\u309f\u30a0-\u30ff]/.test(text)) return 'ja';
  if (/[\uac00-\ud7af]/.test(text)) return 'ko';
  return 'en';
}
