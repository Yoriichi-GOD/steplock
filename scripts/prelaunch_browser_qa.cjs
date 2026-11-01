// Actual local Chromium acceptance. No cloud/provider calls or personal browser profile.
const path=require('node:path');const fs=require('node:fs');const assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..');const qa=path.join(root,'runtime/browser_qa');
process.env.PLAYWRIGHT_BROWSERS_PATH=path.join(qa,'browsers');
const {chromium}=require(path.join(qa,'node_modules/playwright'));
const base=process.env.STEPLOCK_QA_ORIGIN||'http://127.0.0.1:62401';
const out=path.join(root,'runtime/qa/prelaunch');fs.mkdirSync(out,{recursive:true});
(async()=>{
 const browser=await chromium.launch({headless:true});const context=await browser.newContext({viewport:{width:1440,height:1000}});const page=await context.newPage();const errors=[];const remote=[];const checks=[];
 page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>{if(/^https?:/.test(r.url())&&!r.url().startsWith(base))remote.push(r.url())});
 const screenshot=async name=>page.screenshot({path:path.join(out,name+'.png'),fullPage:false});
 const measure=async()=>page.evaluate(()=>({viewport:innerWidth,document_width:document.documentElement.scrollWidth,broken_images:[...document.images].filter(i=>!i.complete||!i.naturalWidth).map(i=>i.getAttribute('src')),paints:performance.getEntriesByType('paint').map(e=>({name:e.name,start_ms:e.startTime})),navigation:performance.getEntriesByType('navigation').map(e=>({dom_content_loaded_ms:e.domContentLoadedEventEnd,load_ms:e.loadEventEnd}))}));
 try{
  await page.goto(base,{waitUntil:'networkidle'});await page.getByRole('link',{name:'Try interactive demo',exact:false}).waitFor();
  await page.locator('.hero-copy').waitFor();await page.waitForTimeout(1200);await screenshot('desktop-hero');
  const initial=await measure();checks.push({check:'desktop_initial',...initial});assert(initial.document_width<=1440);assert.deepEqual(initial.broken_images,[]);
  await page.getByRole('button',{name:'2D',exact:true}).click();await page.locator('.technical-assembly').first().waitFor();await screenshot('technical-2d');
  await page.getByRole('button',{name:/Explode illustration/}).click();await page.getByRole('button',{name:/Assemble illustration/}).waitFor();
  await page.getByRole('button',{name:'3D',exact:true}).click();await page.waitForTimeout(1600);
  const canvas=page.locator('.hero-model canvas');
  if(await canvas.count()){
   await screenshot('interactive-3d');await canvas.evaluate(c=>c.dispatchEvent(new Event('webglcontextlost',{cancelable:true})));await page.getByText('3D unavailable',{exact:false}).waitFor();checks.push({check:'webgl_context_loss_fallback',pass:true});
  }else{assert(await page.locator('.technical-assembly').count());checks.push({check:'webgl_unavailable_fallback',pass:true})}
  await page.getByRole('button',{name:/Illustrate wrong order/}).click();await page.getByText('The cover depends on the spacer.',{exact:false}).waitFor();
  await page.screenshot({path:path.join(out,'full-landing.png'),fullPage:true});
  for(const width of [360,390,768,1280,1920]){await page.setViewportSize({width,height:900});await page.evaluate(()=>scrollTo(0,0));await page.waitForTimeout(150);const result=await measure();assert(result.document_width<=width+1,JSON.stringify(result));assert.deepEqual(result.broken_images,[]);checks.push({check:'landing_viewport',...result});if(width===390)await screenshot('mobile-hero')}
  await page.setViewportSize({width:1440,height:1000});await page.goto(base+'/app',{waitUntil:'networkidle'});await page.getByRole('heading',{name:'The full workbench.'}).waitFor();assert(await page.getByText('Owner access is not configured',{exact:false}).count());checks.push({check:'private_workspace_gate',pass:true});
  await page.goto(base+'/demo',{waitUntil:'networkidle'});await page.getByRole('button',{name:/Run inspection/}).waitFor();assert.equal((await page.getByTestId('demo-verdict').textContent()).trim(),'PENDING');
  for(const [title,verdict,event] of [['Normal','PASS','checkpoint'],['Wrong Component','HOLD_FOR_REVIEW','wrong component'],['Wrong Order','HOLD_FOR_REVIEW','order violation'],['Correction','PASS','corrected']]){
   await page.getByRole('button',{name:new RegExp(title)}).click();assert.equal((await page.getByTestId('demo-verdict').textContent()).trim(),'PENDING');
   const created=page.waitForResponse(r=>r.url()===base+'/api/public/demo/sessions'&&r.request().method()==='POST');await page.getByRole('button',{name:/Run inspection/}).click();const response=await created;assert.equal(response.status(),201);const session=await response.json();
   await page.waitForFunction(()=>document.querySelector('.demo-evidence .instrument-heading')?.textContent.includes('REPLAY COMPLETE'),null,{timeout:20000});assert.equal((await page.getByTestId('demo-verdict').textContent()).trim(),verdict);
   await page.locator('.demo-source-image img').waitFor();await page.waitForFunction(()=>document.querySelector('.demo-source-image img')?.naturalWidth>0);await screenshot('demo-'+title.toLowerCase().replaceAll(' ','-'));
   assert((await page.locator('.demo-timeline').innerText()).toLowerCase().includes(event));
   const evidence=page.locator('.demo-timeline button:not([disabled])').last();await evidence.click();await page.locator('.evidence-detail').waitFor();await page.getByRole('button',{name:'Source frame',exact:true}).click();await page.waitForFunction(()=>document.querySelector('.demo-source-image img')?.naturalWidth>0);await screenshot('source-evidence');
   const own=await page.request.get(base+`/api/public/demo/sessions/${session.session_id}`,{headers:{Authorization:'Bearer '+session.access_token}});assert.equal(own.status(),200);
   const foreign=await page.request.get(base+`/api/public/demo/sessions/${session.session_id}`,{headers:{Authorization:'Bearer different-visitor'}});assert.equal(foreign.status(),404);
   checks.push({check:'actual_replay',scenario:title,verdict,source_frame_loaded:true,foreign_session_denied:true});
  }
  for(const width of [360,390,768,1280,1920]){await page.setViewportSize({width,height:900});const result=await measure();assert(result.document_width<=width+1,JSON.stringify(result));checks.push({check:'demo_viewport',...result});if(width===390)await screenshot('mobile-demo')}
  await page.setViewportSize({width:1280,height:720});await page.route('**/api/public/demo/sessions/**',route=>route.abort());await page.getByTestId('demo-verdict').filter({hasText:'SOURCE LOST'}).waitFor({timeout:8000});assert.equal(await page.locator('.demo-steps .confirmed').count(),0);await screenshot('connection-loss');checks.push({check:'source_loss_suppresses_stale_pass_and_green',pass:true});await page.unroute('**/api/public/demo/sessions/**');
  await page.reload({waitUntil:'networkidle'});assert.equal((await page.getByTestId('demo-verdict').textContent()).trim(),'PENDING');checks.push({check:'refresh_is_neutral',pass:true});
  const offline=await browser.newContext({viewport:{width:390,height:844},reducedMotion:'reduce'});const offlinePage=await offline.newPage();await offlinePage.route('**/api/**',r=>r.abort());await offlinePage.goto(base+'/demo',{waitUntil:'networkidle'});await offlinePage.getByRole('alert').waitFor();assert.equal((await offlinePage.getByTestId('demo-verdict').textContent()).trim(),'PENDING');assert(await offlinePage.getByRole('button',{name:/Run inspection/}).isDisabled());await offlinePage.screenshot({path:path.join(out,'startup-no-backend.png')});checks.push({check:'clean_start_no_backend',pass:true});await offlinePage.goto(base,{waitUntil:'networkidle'});await offlinePage.waitForTimeout(600);assert.equal(await offlinePage.locator('.hero-model canvas').count(),0);assert(await offlinePage.locator('.technical-assembly').count());checks.push({check:'reduced_motion_2d',pass:true});await offline.close();
  assert.equal((await page.request.post(base+'/api/sessions',{data:{source_kind:'LIVE_TAGGED'}})).status(),403);assert.equal((await page.request.post(base+'/api/recipes',{data:{}})).status(),403);assert.equal((await page.request.post(base+'/api/sessions/any/agent/explain',{data:{}})).status(),403);
  assert.deepEqual(errors,[]);assert.deepEqual(remote,[]);checks.push({check:'uncaught_errors_and_external_visual_requests',errors,remote});
  fs.writeFileSync(path.join(out,'acceptance.json'),JSON.stringify({at:new Date().toISOString(),origin:base,browser:browser.version(),result:'PASS',checks},null,2));console.log(JSON.stringify({result:'PASS',checks:checks.length,output:out}));
 }catch(error){await screenshot('failure').catch(()=>{});fs.writeFileSync(path.join(out,'acceptance-failure.json'),JSON.stringify({at:new Date().toISOString(),error:String(error),errors,remote,checks},null,2));throw error}finally{await browser.close()}
})().catch(e=>{console.error(e);process.exit(1)});
