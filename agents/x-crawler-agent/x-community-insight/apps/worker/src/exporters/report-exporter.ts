import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { CategorySummary, ClassifiedFeedback } from '../analyzer/feedback-analyzer.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const EXPORTS_DIR = path.resolve(__dirname, '../../../../data/exports');

if (!fs.existsSync(EXPORTS_DIR)) {
  fs.mkdirSync(EXPORTS_DIR, { recursive: true });
}

export interface ReportData {
  competitorName: string;
  dateRangeStart: string;
  dateRangeEnd: string;
  totalPosts: number;
  totalReplies: number;
  completenessScore: number;
  summaries: CategorySummary[];
  classified: ClassifiedFeedback[];
  topPosts?: Array<{ url: string; content: string; likeCount: number; replyCount: number; repostCount: number; postedAt: string }>;
}

/**
 * 匯出 Markdown 報告
 */
export function exportMarkdown(data: ReportData): string {
  const timestamp = new Date().toISOString().slice(0, 10);
  const filename = `report_${data.competitorName}_${timestamp}.md`;
  const filePath = path.join(EXPORTS_DIR, filename);

  const positiveCount = data.classified.filter(c => c.sentiment === 'positive').length;
  const negativeCount = data.classified.filter(c => c.sentiment === 'negative').length;
  const neutralCount = data.classified.filter(c => c.sentiment === 'neutral').length;
  const total = data.classified.length || 1;

  let md = `# 競品社群反饋分析報告

## 一、分析範圍

| 項目 | 內容 |
|------|------|
| 競品名稱 | ${data.competitorName} |
| 分析期間 | ${data.dateRangeStart} ~ ${data.dateRangeEnd} |
| 蒐集貼文數 | ${data.totalPosts} |
| 蒐集留言數 | ${data.totalReplies} |
| 資料完整度 | ${data.completenessScore}% |
| 報告產出時間 | ${new Date().toISOString()} |

## 二、整體社群情緒

| 情緒 | 比例 |
|------|------|
| 正面 | ${((positiveCount / total) * 100).toFixed(1)}% (${positiveCount} 則) |
| 負面 | ${((negativeCount / total) * 100).toFixed(1)}% (${negativeCount} 則) |
| 中性 | ${((neutralCount / total) * 100).toFixed(1)}% (${neutralCount} 則) |

`;

  // 高熱度貼文
  if (data.topPosts && data.topPosts.length > 0) {
    md += `## 三、高熱度貼文

| # | 摘要 | 發文時間 | 按讚 | 留言 | 轉貼 | 連結 |
|---|------|---------|------|------|------|------|
`;
    data.topPosts.slice(0, 10).forEach((p, i) => {
      const summary = p.content.slice(0, 40).replace(/\|/g, '\\|').replace(/\n/g, ' ');
      md += `| ${i + 1} | ${summary} | ${p.postedAt?.slice(0, 10) || '-'} | ${p.likeCount} | ${p.replyCount} | ${p.repostCount} | [連結](${p.url}) |\n`;
    });
    md += '\n';
  }

  // 反饋分類
  md += `## 四、玩家反饋分類

| 分類 | 數量 | 情緒 | 重要程度 | 代表留言 | 建議 |
|------|---:|------|---------|---------|------|
`;
  for (const s of data.summaries) {
    const comment = (s.representativeComments[0] || '').slice(0, 40).replace(/\|/g, '\\|').replace(/\n/g, ' ');
    md += `| ${s.name} | ${s.count} | ${s.sentiment} | ${s.severity} | "${comment}" | ${s.suggestion} |\n`;
  }

  // 產品建議
  md += `
## 五、產品建議

### 短期可處理事項
`;
  const highSeverity = data.summaries.filter(s => s.severity === '高');
  highSeverity.forEach(s => { md += `- **${s.name}** (${s.count} 則): ${s.suggestion}\n`; });

  md += `
### 中期優化方向
`;
  const medSeverity = data.summaries.filter(s => s.severity === '中');
  medSeverity.forEach(s => { md += `- **${s.name}** (${s.count} 則): ${s.suggestion}\n`; });

  md += `
### 長期產品機會
`;
  const lowSeverity = data.summaries.filter(s => s.severity === '低');
  lowSeverity.forEach(s => { md += `- **${s.name}** (${s.count} 則): ${s.suggestion}\n`; });

  md += `
## 六、原始資料索引

`;
  const allUrls = data.classified.filter(c => c.url).slice(0, 20);
  allUrls.forEach(c => {
    md += `- [${c.category}] ${c.content.slice(0, 30)}... — [連結](${c.url})\n`;
  });

  fs.writeFileSync(filePath, md, 'utf-8');
  return filePath;
}

/**
 * 匯出 JSON 報告
 */
export function exportJSON(data: ReportData): string {
  const timestamp = new Date().toISOString().slice(0, 10);
  const filename = `report_${data.competitorName}_${timestamp}.json`;
  const filePath = path.join(EXPORTS_DIR, filename);
  fs.writeFileSync(filePath, JSON.stringify(data, null, 2), 'utf-8');
  return filePath;
}

/**
 * 匯出 CSV 報告
 */
export function exportCSV(data: ReportData): string {
  const timestamp = new Date().toISOString().slice(0, 10);
  const filename = `report_${data.competitorName}_${timestamp}.csv`;
  const filePath = path.join(EXPORTS_DIR, filename);

  const header = '分類,數量,情緒,重要程度,代表留言,建議\n';
  const rows = data.summaries.map(s => {
    const comment = (s.representativeComments[0] || '').replace(/"/g, '""').replace(/\n/g, ' ');
    return `"${s.name}",${s.count},"${s.sentiment}","${s.severity}","${comment}","${s.suggestion}"`;
  }).join('\n');

  fs.writeFileSync(filePath, '\uFEFF' + header + rows, 'utf-8');
  return filePath;
}
