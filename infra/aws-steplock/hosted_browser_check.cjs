// Hosted acceptance uses public generated examples only; no AWS/model credentials.
const path=require('node:path'),fs=require('node:fs'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'../..');
process.env.PLAYWRIGHT_BROWSERS_PATH=path.join(root,'runtime/browser_qa/browsers');
const {chromium}=require(path.join(root,'runtime/browser_qa/node_modules/playwright'));
const base=process.argv[2];assert(base&&new URL(base).protocol==='https:','Provide the actual HTTPS endpoint');
const out=path.join(root,'runtime/aws-deploy-20261102/browser');fs.mkdirSync(out,{recursive:true});
(async()=>{
 const browser=await chromium.launch({headless:true}),context=await browser.newContext({viewport:{width:1280,height:720}}),page=await context.newPage();
 const errors=[],remote=[],checks=[];page.on('pageerror',e=>errors.push(e.message));
 page.on('request',r=>{if(/^https?:/.test(r.url())&&new URL(r.url()).origin!==base)remote.push(new URL(r.url()).origin);});
 try{
  const health=await page.request.get(base+'/api/health');assert.equal(health.status(),200);
  const headers=health.headers();assert(headers['strict-transport-security']?.includes('max-age='));assert.equal(headers['x-frame-options'],'DENY');assert.equal(headers['x-content-type-options'],'nosniff');
  const config=await (await page.request.get(base+'/api/public/config')).json();assert(config.public_mode);assert.equal(config.owner_access_enabled,false);assert.equal(config.contact_email,null);
  for(const route of ['/api/recipes','/api/agent/health','/openapi.json'])assert.equal((await page.request.get(base+route)).status(),403);
  assert.equal((await page.request.get(base+'/api/public/config',{headers:{Origin:'https://example.invalid'}})).status(),403);
  checks.push({test:'https_public_boundary',pass:true,hsts:headers['strict-transport-security'],owner_access:false,contact_configured:false});
  for(const [width,height] of [[1280,720],[390,844],[320,740]]){
   await page.setViewportSize({width,height});await page.goto(base,{waitUntil:'networkidle'});await page.locator('h1').waitFor();
   const geometry=await page.evaluate(()=>({viewport:innerWidth,documentWidth:document.documentElement.scrollWidth,barBorder:getComputedStyle(document.querySelector('.story-instrument')).borderTopWidth,visualTop:document.querySelector('.story-visual').getBoundingClientRect().top,mode:document.querySelector('.mode-switch button[aria-pressed="true"]')?.textContent}));
   assert(geometry.documentWidth<=width);if(width<768){assert(Math.abs(geometry.visualTop-height/2)<2);assert.equal(geometry.barBorder,'0px');}
   checks.push({test:'landing_viewport',...geometry});if(width!==320)await page.screenshot({path:path.join(out,`landing-${width}.png`)});
   await page.goto(base+'/demo',{waitUntil:'networkidle'});assert.equal(await page.getByTestId('demo-verdict').getAttribute('data-status'),'PENDING');assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
   checks.push({test:'demo_viewport',width,status:'PENDING'});
  }
  await page.setViewportSize({width:1280,height:720});await page.goto(base+'/app',{waitUntil:'networkidle'});await page.getByRole('heading',{name:'The full workbench.'}).waitFor();checks.push({test:'private_workspace_gate',pass:true});
  await page.goto(base+'/demo',{waitUntil:'networkidle'});
  const responsePromise=page.waitForResponse(r=>r.url()===base+'/api/public/demo/sessions'&&r.request().method()==='POST');const began=Date.now();await page.getByRole('button',{name:/Run inspection/}).click();
  assert.equal((await responsePromise).status(),201);
  await page.waitForFunction(()=>document.querySelector('.demo-evidence .instrument-heading')?.textContent.includes('REPLAY COMPLETE'),null,{timeout:35000});
  assert.equal(await page.getByTestId('demo-verdict').getAttribute('data-status'),'PASS');await page.locator('.demo-source-image img').waitFor();
  await page.waitForFunction(()=>document.querySelector('.demo-source-image img')?.naturalWidth>0);
  const elapsed=Date.now()-began,style=await page.locator('.demo-source-image img').evaluate(e=>({filter:getComputedStyle(e).filter,opacity:getComputedStyle(e).opacity}));assert.deepEqual(style,{filter:'none',opacity:'1'});
  checks.push({test:'actual_generated_normal',decision:'PASS',completion_ms:elapsed,runtime:await page.locator('.public-runtime').innerText(),ledger:await page.locator('.demo-evidence .instrument-heading').innerText(),evidence_style:style});
  await page.screenshot({path:path.join(out,'actual-normal-pass.png')});
  const held=[];await page.route('**/api/public/demo/sessions/*',route=>route.request().method()==='GET'?held.push(route):route.continue());const lostAt=Date.now();
  await page.getByTestId('demo-verdict').filter({hasText:'SOURCE LOST'}).waitFor({timeout:8000});assert.equal(await page.locator('.demo-steps .confirmed').count(),0);assert.equal(await page.locator('.public-verdict.pass').count(),0);
  checks.push({test:'stalled_heartbeat_clears_pass',observed_ms:Date.now()-lostAt,confirmed_steps:0});await page.screenshot({path:path.join(out,'source-loss.png')});
  await page.unroute('**/api/public/demo/sessions/*');await Promise.allSettled(held.map(r=>r.abort()));
  await page.waitForFunction(()=>document.querySelector('[data-testid="demo-verdict"]')?.getAttribute('data-status')==='PASS',null,{timeout:12000});
  const removed=page.waitForResponse(r=>r.request().method()==='DELETE'&&r.url().includes('/api/public/demo/sessions/'));await page.getByRole('button',{name:'Reset',exact:true}).click();assert.equal((await removed).status(),200);assert.equal(await page.getByTestId('demo-verdict').getAttribute('data-status'),'PENDING');
  checks.push({test:'reconnect_and_delete_reset',pass:true});await page.reload({waitUntil:'networkidle'});assert.equal(await page.getByTestId('demo-verdict').getAttribute('data-status'),'PENDING');
  const offlineContext=await browser.newContext({viewport:{width:1280,height:720}}),offline=await offlineContext.newPage();await offline.route('**/api/**',r=>r.abort());await offline.goto(base+'/demo',{waitUntil:'networkidle'});await offline.locator('.demo-error').waitFor();assert.equal(await offline.getByTestId('demo-verdict').getAttribute('data-status'),'PENDING');assert(await offline.getByRole('button',{name:/Run inspection/}).isDisabled());await offline.screenshot({path:path.join(out,'unavailable-backend.png')});await offlineContext.close();checks.push({test:'clean_start_without_api',pass:true});
  await page.setViewportSize({width:390,height:844});await page.screenshot({path:path.join(out,'demo-phone-neutral.png')});assert.deepEqual(errors,[]);assert.deepEqual([...new Set(remote)],[]);
  const receipt={result:'PASS',endpoint:base,population:'SYNTHETIC_FIXTURE',checks,page_errors:errors,external_origins:[...new Set(remote)],limits:'Browser-emulated viewports, one measured run; no factory accuracy or physical-phone performance claim.'};fs.writeFileSync(path.join(out,'acceptance.json'),JSON.stringify(receipt,null,2));console.log(JSON.stringify(receipt));
 }catch(e){await page.screenshot({path:path.join(out,'failure.png')}).catch(()=>{});fs.writeFileSync(path.join(out,'partial.json'),JSON.stringify({checks,errors,remote,error:e.message},null,2));throw e;}finally{await context.close();await browser.close();}
})().catch(e=>{console.error(e.stack);process.exitCode=1});
