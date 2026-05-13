import { Command } from 'commander';
import { addCompetitor, getCompetitors, getCompetitorByName, createCrawlJob, updateCrawlJob, getPostsByCompetitor, getAllRepliesWithPosts, getAllPosts } from './database/repository.js';
import { initDatabase } from './database/migrate.js';
import { launchBrowser, closeBrowser, loadSavedState, getPage } from './crawler/browser.js';
import { crawlPost } from './crawler/post-crawler.js';
import { crawlAccount } from './crawler/account-crawler.js';
import { crawlHashtag } from './crawler/hashtag-crawler.js';
import { getAnalyzer } from './analyzer/feedback-analyzer.js';
import { exportMarkdown, exportJSON, exportCSV, ReportData } from './exporters/report-exporter.js';

// 確保資料庫已初始化
initDatabase();

const program = new Command();
program.name('x-community-insight').description('X/Twitter 競品社群爬蟲與玩家反饋分析工具').version('1.0.0');

// 新增競品
program
  .command('competitor:add')
  .description('新增競品帳號')
  .requiredOption('--name <name>', '競品名稱')
  .requiredOption('--url <url>', 'X 帳號網址')
  .action((opts) => {
    const handle = opts.url.split('/').pop() || '';
    addCompetitor(opts.name, opts.url, handle);
    console.log(`✅ 已新增競品: ${opts.name} (${opts.url})`);
  });

// 列出競品
program
  .command('competitor:list')
  .description('列出所有競品')
  .action(() => {
    const list = getCompetitors() as any[];
    if (list.length === 0) {
      console.log('尚無競品資料');
      return;
    }
    console.log('\n競品列表:');
    list.forEach((c: any) => {
      console.log(`  - ${c.name} | ${c.x_url} | 建立於 ${c.created_at}`);
    });
  });

// 爬取帳號
program
  .command('crawl:account')
  .description('爬取競品帳號頁面')
  .requiredOption('--competitor <name>', '競品名稱')
  .option('--max-posts <n>', '最大貼文數', '100')
  .option('--days <n>', '近 N 天', '')
  .action(async (opts) => {
    const comp = getCompetitorByName(opts.competitor);
    if (!comp) {
      console.error(`❌ 找不到競品: ${opts.competitor}`);
      process.exit(1);
    }

    const job = createCrawlJob(comp.id, comp.x_url, 'account', { maxPosts: parseInt(opts.maxPosts) });
    const jobId = Number(job.lastInsertRowid);

    console.log(`🔄 開始爬取帳號: ${comp.x_url}`);

    try {
      const ctx = await loadSavedState();
      const page = await ctx.newPage();

      const result = await crawlAccount(page, {
        url: comp.x_url,
        maxPosts: parseInt(opts.maxPosts),
        days: opts.days ? parseInt(opts.days) : undefined,
        jobId,
        competitorId: comp.id,
      });

      updateCrawlJob(jobId, { status: 'completed', completenessScore: 100 });
      console.log(`✅ 爬取完成: 蒐集 ${result.postsCollected} 篇貼文`);
    } catch (err: any) {
      updateCrawlJob(jobId, { status: 'failed', errorMessage: err.message });
      console.error(`❌ 爬取失敗: ${err.message}`);
    } finally {
      await closeBrowser();
    }
  });

// 爬取指定貼文
program
  .command('crawl:post')
  .description('爬取指定貼文及留言')
  .requiredOption('--url <url>', '貼文網址')
  .option('--passes <n>', '爬取輪數', '3')
  .option('--max-replies <n>', '最大留言數', '500')
  .option('--competitor <name>', '關聯競品名稱')
  .action(async (opts) => {
    const comp = opts.competitor ? getCompetitorByName(opts.competitor) : null;
    const job = createCrawlJob(comp?.id || null, opts.url, 'post', {
      maxReplies: parseInt(opts.maxReplies),
      crawlPasses: parseInt(opts.passes),
    });
    const jobId = Number(job.lastInsertRowid);

    console.log(`🔄 開始爬取貼文: ${opts.url}`);

    try {
      const ctx = await loadSavedState();
      const page = await ctx.newPage();

      const result = await crawlPost(page, {
        url: opts.url,
        maxReplies: parseInt(opts.maxReplies),
        crawlPasses: parseInt(opts.passes),
        jobId,
        competitorId: comp?.id,
      });

      updateCrawlJob(jobId, { status: 'completed', completenessScore: result.completenessScore });
      console.log(`✅ 爬取完成: 蒐集 ${result.repliesCollected} 則留言, 完整度 ${result.completenessScore}%`);
    } catch (err: any) {
      updateCrawlJob(jobId, { status: 'failed', errorMessage: err.message });
      console.error(`❌ 爬取失敗: ${err.message}`);
    } finally {
      await closeBrowser();
    }
  });

// 爬取 Hashtag
program
  .command('crawl:hashtag')
  .description('搜尋指定 hashtag 的貼文')
  .requiredOption('--tag <hashtag>', 'Hashtag（例如 ゴールデンホイヤー）')
  .option('--max-posts <n>', '最大貼文數', '30')
  .option('--competitor <name>', '關聯競品名稱')
  .action(async (opts) => {
    const comp = opts.competitor ? getCompetitorByName(opts.competitor) : null;
    const tag = opts.tag.startsWith('#') ? opts.tag : `#${opts.tag}`;
    const job = createCrawlJob(comp?.id || null, `https://x.com/search?q=${encodeURIComponent(tag)}`, 'account', { maxPosts: parseInt(opts.maxPosts) });
    const jobId = Number(job.lastInsertRowid);

    console.log(`🔄 開始搜尋 hashtag: ${tag}`);

    try {
      const ctx = await loadSavedState();
      const page = await ctx.newPage();

      const result = await crawlHashtag(page, {
        hashtag: opts.tag,
        maxPosts: parseInt(opts.maxPosts),
        jobId,
        competitorId: comp?.id,
      });

      updateCrawlJob(jobId, { status: 'completed', completenessScore: 100 });
      console.log(`✅ 搜尋完成: 蒐集 ${result.postsCollected} 篇貼文`);
    } catch (err: any) {
      updateCrawlJob(jobId, { status: 'failed', errorMessage: err.message });
      console.error(`❌ 搜尋失敗: ${err.message}`);
    } finally {
      await closeBrowser();
    }
  });

// 分析
program
  .command('analyze')
  .description('分析玩家反饋')
  .option('--competitor <name>', '競品名稱')
  .option('--days <n>', '近 N 天', '30')
  .action((opts) => {
    const comp = opts.competitor ? getCompetitorByName(opts.competitor) : null;
    const replies = getAllRepliesWithPosts(comp?.id) as any[];

    if (replies.length === 0) {
      console.log('⚠️ 無留言資料可分析');
      return;
    }

    const analyzer = getAnalyzer('local');
    const items = replies.map((r: any) => ({
      content: r.content || '',
      authorHandle: r.author_handle || '',
      url: r.url || '',
      repliedAt: r.replied_at || '',
    }));

    const classified = analyzer.classify(items);
    const summaries = analyzer.summarize(classified);

    console.log('\n📊 反饋分析結果:\n');
    console.log('分類 | 數量 | 情緒 | 重要程度');
    console.log('-----|------|------|--------');
    summaries.forEach(s => {
      console.log(`${s.name} | ${s.count} | ${s.sentiment} | ${s.severity}`);
    });
  });

// 匯出報告
program
  .command('export')
  .description('匯出分析報告')
  .option('--competitor <name>', '競品名稱')
  .option('--format <fmt>', '格式: markdown | json | csv', 'markdown')
  .option('--days <n>', '近 N 天', '30')
  .action((opts) => {
    const comp = opts.competitor ? getCompetitorByName(opts.competitor) : null;
    const replies = getAllRepliesWithPosts(comp?.id) as any[];
    const posts = comp ? getPostsByCompetitor(comp.id) as any[] : [];

    if (replies.length === 0) {
      console.log('⚠️ 無資料可匯出');
      return;
    }

    const analyzer = getAnalyzer('local');
    const items = replies.map((r: any) => ({
      content: r.content || '',
      authorHandle: r.author_handle || '',
      url: r.url || '',
      repliedAt: r.replied_at || '',
    }));

    const classified = analyzer.classify(items);
    const summaries = analyzer.summarize(classified);

    const now = new Date();
    const daysAgo = new Date(now.getTime() - parseInt(opts.days) * 86400000);

    const reportData: ReportData = {
      competitorName: comp?.name || '全部',
      dateRangeStart: daysAgo.toISOString().slice(0, 10),
      dateRangeEnd: now.toISOString().slice(0, 10),
      totalPosts: posts.length,
      totalReplies: replies.length,
      completenessScore: 80,
      summaries,
      classified,
    };

    let filePath: string;
    switch (opts.format) {
      case 'json':
        filePath = exportJSON(reportData);
        break;
      case 'csv':
        filePath = exportCSV(reportData);
        break;
      default:
        filePath = exportMarkdown(reportData);
    }

    console.log(`✅ 報告已匯出: ${filePath}`);
  });

// 登入輔助
program
  .command('login')
  .description('開啟瀏覽器讓使用者手動登入 X')
  .action(async () => {
    console.log('🌐 開啟瀏覽器，請手動登入 X...');
    console.log('   登入完成後，按 Ctrl+C 關閉，登入狀態會自動保存。');

    const ctx = await launchBrowser();
    const page = await ctx.newPage();
    await page.goto('https://x.com/login');

    // 等待使用者手動操作
    await new Promise(() => {}); // 永久等待直到 Ctrl+C
  });

program.parse();
