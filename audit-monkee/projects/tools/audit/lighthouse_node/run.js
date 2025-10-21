import lighthouse from 'lighthouse';
import chromeLauncher from 'chrome-launcher';

const url = process.argv[2];
if (!url) {
  console.error('Usage: node run.js <url>');
  process.exit(2);
}

const opts = {
  logLevel: 'info',
  output: 'json',
  onlyCategories: ['performance','accessibility','best-practices','seo'],
  port: 0,
};
const config = null; // default

(async () => {
  const chrome = await chromeLauncher.launch({chromeFlags: ['--headless=new', '--no-sandbox', '--disable-gpu']});
  try {
    const results = await lighthouse(url, { ...opts, port: chrome.port }, config);
    console.log(JSON.stringify(results.lhr));
  } catch (e) {
    console.error('LH error:', e?.message || e);
    process.exit(1);
  } finally {
    await chrome.kill();
  }
})();
