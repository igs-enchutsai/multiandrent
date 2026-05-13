import { chromium, Browser, BrowserContext, Page } from 'playwright';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const PROFILE_DIR = process.env.BROWSER_PROFILE_DIR || path.resolve(__dirname, '../../../../data/browser-profile');

let browser: Browser | null = null;
let context: BrowserContext | null = null;

export async function launchBrowser(): Promise<BrowserContext> {
  if (context) return context;

  browser = await chromium.launch({
    headless: false, // 需要可見瀏覽器以便手動登入
    args: ['--disable-blink-features=AutomationControlled'],
  });

  context = await browser.newContext({
    storageState: undefined,
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    viewport: { width: 1280, height: 900 },
  });

  return context;
}

export async function getPage(): Promise<Page> {
  const ctx = await launchBrowser();
  const page = await ctx.newPage();
  return page;
}

export async function closeBrowser(): Promise<void> {
  if (context) {
    // Save storage state for reuse
    try {
      const statePath = path.resolve(PROFILE_DIR, 'state.json');
      await context.storageState({ path: statePath });
    } catch { /* ignore */ }
    await context.close();
    context = null;
  }
  if (browser) {
    await browser.close();
    browser = null;
  }
}

export async function loadSavedState(): Promise<BrowserContext> {
  const statePath = path.resolve(PROFILE_DIR, 'state.json');
  
  browser = await chromium.launch({
    headless: false,
    args: ['--disable-blink-features=AutomationControlled'],
  });

  try {
    context = await browser.newContext({
      storageState: statePath,
      userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
      viewport: { width: 1280, height: 900 },
    });
  } catch {
    // No saved state, create fresh context
    context = await browser.newContext({
      userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
      viewport: { width: 1280, height: 900 },
    });
  }

  return context;
}
