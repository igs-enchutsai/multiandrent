import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import YAML from 'yaml';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const RULES_PATH = path.resolve(__dirname, '../../../../config/feedback-rules.yaml');

export interface FeedbackCategory {
  name: string;
  description: string;
  severity_weight: number;
  keywords: string[];
}

export interface ClassifiedFeedback {
  category: string;
  content: string;
  authorHandle: string;
  url: string;
  sentiment: 'positive' | 'negative' | 'neutral';
  repliedAt: string;
}

export interface CategorySummary {
  name: string;
  count: number;
  sentiment: string;
  severity: string;
  representativeComments: string[];
  urls: string[];
  suggestion: string;
}

/**
 * 分析器介面 — 可擴充 AI 分析
 */
export interface AnalyzerProvider {
  classify(items: Array<{ content: string; authorHandle: string; url: string; repliedAt: string }>): ClassifiedFeedback[];
  summarize(classified: ClassifiedFeedback[]): CategorySummary[];
}

/**
 * 本地規則式分析器
 */
export class LocalRuleAnalyzer implements AnalyzerProvider {
  private categories: FeedbackCategory[];

  constructor() {
    const raw = fs.readFileSync(RULES_PATH, 'utf-8');
    const config = YAML.parse(raw);
    this.categories = config.categories;
  }

  classify(items: Array<{ content: string; authorHandle: string; url: string; repliedAt: string }>): ClassifiedFeedback[] {
    const results: ClassifiedFeedback[] = [];

    for (const item of items) {
      const lower = item.content.toLowerCase();
      let matched = false;

      for (const cat of this.categories) {
        const hit = cat.keywords.some(kw => lower.includes(kw.toLowerCase()));
        if (hit) {
          results.push({
            category: cat.name,
            content: item.content,
            authorHandle: item.authorHandle,
            url: item.url || '',
            sentiment: this.detectSentiment(cat.name),
            repliedAt: item.repliedAt,
          });
          matched = true;
          break; // 每則留言只歸入第一個匹配的分類
        }
      }

      if (!matched) {
        results.push({
          category: '其他',
          content: item.content,
          authorHandle: item.authorHandle,
          url: item.url || '',
          sentiment: 'neutral',
          repliedAt: item.repliedAt,
        });
      }
    }

    return results;
  }

  summarize(classified: ClassifiedFeedback[]): CategorySummary[] {
    const groups = new Map<string, ClassifiedFeedback[]>();

    for (const item of classified) {
      const list = groups.get(item.category) || [];
      list.push(item);
      groups.set(item.category, list);
    }

    const summaries: CategorySummary[] = [];

    for (const [name, items] of groups) {
      const cat = this.categories.find(c => c.name === name);
      const severity = cat ? this.severityLabel(cat.severity_weight) : '低';

      // 取代表性留言（按讚最多或最早出現的前 3 則）
      const representative = items.slice(0, 3).map(i => i.content.slice(0, 80));
      const urls = items.slice(0, 5).map(i => i.url).filter(Boolean);

      const sentimentCounts = { positive: 0, negative: 0, neutral: 0 };
      items.forEach(i => sentimentCounts[i.sentiment]++);
      const dominantSentiment = Object.entries(sentimentCounts).sort((a, b) => b[1] - a[1])[0][0];

      summaries.push({
        name,
        count: items.length,
        sentiment: this.sentimentLabel(dominantSentiment),
        severity,
        representativeComments: representative,
        urls,
        suggestion: this.generateSuggestion(name, items.length),
      });
    }

    return summaries.sort((a, b) => b.count - a.count);
  }

  private detectSentiment(categoryName: string): 'positive' | 'negative' | 'neutral' {
    if (categoryName.includes('正面')) return 'positive';
    if (categoryName.includes('負面') || categoryName.includes('Bug') || categoryName.includes('課金')) return 'negative';
    return 'neutral';
  }

  private severityLabel(weight: number): string {
    if (weight >= 5) return '高';
    if (weight >= 3) return '中';
    return '低';
  }

  private sentimentLabel(s: string): string {
    if (s === 'positive') return '正面';
    if (s === 'negative') return '負面';
    return '中性';
  }

  private generateSuggestion(category: string, count: number): string {
    const suggestions: Record<string, string> = {
      'Bug / 閃退': '優先檢查最新版本穩定性，安排 hotfix',
      '課金 / 商城 / 價格': '檢查禮包 CP 值與玩家感受，考慮調整定價策略',
      '玩法建議': '收集高頻建議，納入產品路線圖評估',
      '正面反饋': '持續維持現有優勢，可作為行銷素材',
      '負面反饋': '深入分析負面原因，制定改善計畫',
      '活動建議': '評估活動獎勵豐富度與玩家期望差距',
      '平衡性問題': '安排數值團隊檢視，考慮平衡性調整',
      '美術 / 角色 / 造型': '收集美術偏好趨勢，回饋設計團隊',
      '效能 / 連線問題': '檢查伺服器負載與客戶端效能瓶頸',
      '客服 / 補償': '檢視客服回應品質與補償政策合理性',
    };
    return suggestions[category] || `共 ${count} 則反饋，建議持續觀察`;
  }
}

// 預留 AI 分析器介面
export class OpenAIAnalyzer implements AnalyzerProvider {
  classify(_items: any[]): ClassifiedFeedback[] {
    throw new Error('OpenAI Analyzer 尚未實作，請設定 OPENAI_API_KEY');
  }
  summarize(_classified: ClassifiedFeedback[]): CategorySummary[] {
    throw new Error('OpenAI Analyzer 尚未實作');
  }
}

export class ClaudeAnalyzer implements AnalyzerProvider {
  classify(_items: any[]): ClassifiedFeedback[] {
    throw new Error('Claude Analyzer 尚未實作');
  }
  summarize(_classified: ClassifiedFeedback[]): CategorySummary[] {
    throw new Error('Claude Analyzer 尚未實作');
  }
}

export function getAnalyzer(provider = 'local'): AnalyzerProvider {
  switch (provider) {
    case 'openai': return new OpenAIAnalyzer();
    case 'claude': return new ClaudeAnalyzer();
    default: return new LocalRuleAnalyzer();
  }
}
