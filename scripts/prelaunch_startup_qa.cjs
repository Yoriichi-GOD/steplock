// Point at Vite preview of the production build, with no API on that origin.
const path = require('node:path');
const fs = require('node:fs');
const assert = require('node:assert/strict');
const root = path.resolve(__dirname, '..');
process.env.PLAYWRIGHT_BROWSERS_PATH = path.join(root, 'runtime/browser_qa/browsers');
const {chromium} = require(path.join(root, 'runtime/browser_qa/node_modules/playwright'));
const base = process.env.STEPLOCK_FRONTEND_ONLY_QA_ORIGIN || 'http://127.0.0.1:62403';
(async () => {
  const browser = await chromium.launch({headless: true});
  const page = await browser.newPage({viewport: {width: 1280, height: 720}});
  try {
    const health = await page.request.get(base + '/api/health');
    assert(!health.headers()['content-type']?.includes('application/json'), 'Use a frontend-only server, without a health API');
    await page.goto(base + '/demo', {waitUntil: 'networkidle'});
    await page.getByRole('alert').waitFor();
    assert.equal((await page.getByTestId('demo-verdict').textContent()).trim(), 'PENDING');
    assert(await page.getByRole('button', {name: /Run inspection/}).isDisabled());
    assert.equal(await page.locator('.demo-steps .confirmed').count(), 0);
    const out = path.join(root, 'runtime/qa/prelaunch');
    await page.screenshot({path: path.join(out, 'startup-frontend-only.png')});
    fs.writeFileSync(path.join(out, 'frontend-only-acceptance.json'), JSON.stringify({at: new Date().toISOString(), origin: base, server: 'Vite production preview only; no backend API on this origin', intercepted_requests: 0, viewport: {width: 1280, height: 720}, result: 'PASS', pending_verdict: true, run_disabled: true, confirmed_green_steps: 0}, null, 2));
    console.log('PASS: production frontend without a backend remains neutral and disabled');
  } finally {
    await browser.close();
  }
})().catch(error => {console.error(error); process.exit(1)});
