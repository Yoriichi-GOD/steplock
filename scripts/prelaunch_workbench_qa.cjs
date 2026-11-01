// Regression of the original workspace after moving it to /app.
const path = require('node:path');
const fs = require('node:fs');
const assert = require('node:assert/strict');
const root = path.resolve(__dirname, '..');
process.env.PLAYWRIGHT_BROWSERS_PATH = path.join(root, 'runtime/browser_qa/browsers');
const {chromium} = require(path.join(root, 'runtime/browser_qa/node_modules/playwright'));
const base = process.env.STEPLOCK_WORKBENCH_QA_ORIGIN || 'http://127.0.0.1:62402';
const out = path.join(root, 'runtime/qa/prelaunch');
fs.mkdirSync(out, {recursive: true});
(async () => {
  const browser = await chromium.launch({headless: true});
  const page = await browser.newPage({viewport: {width: 1280, height: 720}});
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  const checks = [];
  try {
    await page.goto(base + '/app', {waitUntil: 'networkidle'});
    await page.getByRole('button', {name: 'Run example', exact: true}).waitFor();
    assert.equal((await page.getByTestId('decision-status').textContent()).trim(), 'PENDING');
    for (const [example, verdict] of [['normal', 'PASS'], ['wrong_component', 'HOLD']]) {
      await page.getByRole('combobox', {name: 'Select example'}).selectOption(example);
      await page.getByRole('button', {name: 'Run example', exact: true}).click();
      await page.waitForFunction(expected => document.querySelector('[data-testid="decision-status"]')?.textContent.trim() === expected, verdict, {timeout: 20000});
      await page.waitForFunction(() => document.querySelector('.video-stage img')?.naturalWidth > 0);
      await page.screenshot({path: path.join(out, `workbench-${example}.png`)});
      checks.push({check: 'original_workspace_replay', example, verdict, source_loaded: true});
    }
    for (const title of ['Evidence explorer', 'Assembly explorer', 'Evaluation lab', 'Recipe designer', 'Demo kit', 'Procedure studio']) {
      await page.getByRole('button', {name: title, exact: true}).click();
      await page.locator('.workspace-title h1').filter({hasText: title}).waitFor();
      checks.push({check: 'original_workspace_tab', title});
    }
    const width = await page.evaluate(() => document.documentElement.scrollWidth);
    assert(width <= 1280);
    await page.getByRole('combobox', {name: 'Select example'}).selectOption('normal');
    await page.getByRole('button', {name: 'Run example', exact: true}).click();
    await page.getByTestId('decision-status').filter({hasText: 'PASS'}).waitFor({timeout: 20000});
    const held=[];
    await page.route('**/api/sessions/*', route => {held.push(route)});
    await page.getByTestId('decision-status').filter({hasText:'SOURCE LOST'}).waitFor({timeout:6500});
    checks.push({check:'original_workspace_stalled_heartbeat_no_pass',pass:true,request_timeout_ms:2500});
    await page.unroute('**/api/sessions/*');
    for(const route of held)await route.abort().catch(()=>{});
    await page.getByTestId('decision-status').filter({hasText:'PASS',exact:true}).waitFor({timeout:6000});
    await page.route('**/api/sessions/**', route => route.abort());
    await page.getByTestId('decision-status').filter({hasText: 'SOURCE LOST'}).waitFor({timeout: 10000});
    await page.screenshot({path: path.join(out, 'workbench-source-loss.png')});
    checks.push({check: 'original_workspace_source_loss_no_pass', pass: true});
    assert.deepEqual(errors, []);
    fs.writeFileSync(path.join(out, 'workbench-acceptance.json'), JSON.stringify({at: new Date().toISOString(), origin: base, browser: browser.version(), result: 'PASS', checks, errors}, null, 2));
    console.log(JSON.stringify({result: 'PASS', checks: checks.length}));
  } finally {
    await browser.close();
  }
})().catch(error => {console.error(error); process.exit(1)});
