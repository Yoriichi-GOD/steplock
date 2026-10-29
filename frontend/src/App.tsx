import {useCallback,useEffect,useRef,useState} from 'react';
import {Activity,ArrowRight,BookOpen,Camera,Check,ChevronDown,FileJson,FlaskConical,GitBranch,HelpCircle,Layers,Loader2,Play,ScanLine,ShieldCheck,Upload,X} from 'lucide-react';
import {api,authHeaders,BASE,download} from './api/client';
import type {Benchmark,Credentials,EventRecord,Recipe,Scenario,Session,SourceKind} from './api/types';
import {useSession} from './hooks/useSession';
import {Studio} from './pages/Studio';
import {Evidence} from './pages/Evidence';
import {Benchmarks} from './pages/Benchmarks';
import {RecipeBuilder} from './pages/RecipeBuilder';
import {GettingStarted} from './pages/GettingStarted';
import {AssemblyExplorer} from './pages/AssemblyExplorer';

type Page='studio'|'evidence'|'assembly'|'benchmarks'|'recipe'|'kit';
const pages:{id:Page;title:string;icon:typeof ScanLine}[]=[{id:'studio',title:'Procedure studio',icon:ScanLine},{id:'evidence',title:'Evidence explorer',icon:Layers},{id:'assembly',title:'Assembly explorer',icon:Layers},{id:'benchmarks',title:'Evaluation lab',icon:FlaskConical},{id:'recipe',title:'Recipe designer',icon:GitBranch},{id:'kit',title:'Demo kit',icon:BookOpen}];

export default function App(){
  const [page,setPage]=useState<Page>('studio');const [recipes,setRecipes]=useState<Recipe[]>([]);const [recipeKey,setRecipeKey]=useState('tagged_four_part_v1');
  const [scenarios,setScenarios]=useState<Scenario[]>([]);const [example,setExample]=useState('normal');const [benchmark,setBenchmark]=useState<Benchmark|null>(null);
  const [health,setHealth]=useState<{cv_version:string}|null>(null);const [apiUp,setApiUp]=useState(false);const [busy,setBusy]=useState(false);
  const [error,setError]=useState<string|null>(null);const [notice,setNotice]=useState('');const [selected,setSelected]=useState<EventRecord|null>(null);
  const [cameraModal,setCameraModal]=useState(false);const [consent,setConsent]=useState(false);const [cameraMode,setCameraMode]=useState('browser');const [cameraIndex,setCameraIndex]=useState(0);
  const [uploadKind,setUploadKind]=useState<SourceKind>('REPLAY_TAGGED');const [uploadConsent,setUploadConsent]=useState(false);const [uploadModal,setUploadModal]=useState(false);const [file,setFile]=useState<File|null>(null);
  const {credentials,session,connected,error:sessionError,bind,setSession}=useSession();
  const video=useRef<HTMLVideoElement>(null);const stream=useRef<MediaStream|null>(null);const cameraActive=useRef(false);const cameraTimer=useRef<ReturnType<typeof setTimeout>|undefined>(undefined);
  const recipe=recipes.find(r=>r.key===recipeKey)||recipes[0];
  const refreshRecipes=useCallback(()=>{api<Recipe[]>('/api/recipes').then(setRecipes).catch(e=>setError(e.message))},[]);
  useEffect(()=>{
    const controller=new AbortController();let disposed=false;let timer:ReturnType<typeof setTimeout>;
    async function refresh(){try{const h=await api<{cv_version:string}>('/api/health',{signal:controller.signal});if(!disposed){setHealth(h);setApiUp(true)}const b=await api<Benchmark>('/api/benchmarks/latest',{signal:controller.signal});if(!disposed)setBenchmark(b)}catch{if(!disposed)setApiUp(false)}if(!disposed)timer=setTimeout(refresh,5000)}
    refresh();refreshRecipes();api<{scenarios:Scenario[]}>('/api/demo/scenarios',{signal:controller.signal}).then(r=>setScenarios(r.scenarios)).catch(()=>{});
    return()=>{disposed=true;controller.abort();clearTimeout(timer)};
  },[refreshRecipes]);
  function releaseCamera(){cameraActive.current=false;clearTimeout(cameraTimer.current);stream.current?.getTracks().forEach(track=>track.stop());stream.current=null;if(video.current)video.current.srcObject=null}
  useEffect(()=>()=>releaseCamera(),[]);
  async function stopCurrent(){releaseCamera();if(credentials&&session&&['running','source_lost','stopping'].includes(session.state)){await api<Session>(`/api/sessions/${credentials.session_id}/stop`,{method:'POST'},credentials).then(setSession)}}
  async function runExample(id=example){
    setBusy(true);setError(null);setNotice('');setSelected(null);
    try{await stopCurrent();const result=await api<Credentials>('/api/sessions',{method:'POST',body:JSON.stringify({recipe_id:recipeKey,source_kind:'SYNTHETIC_FIXTURE',example_id:id})});bind(result);await api(`/api/sessions/${result.session_id}/start`,{method:'POST',body:JSON.stringify({checkpoint_at_end:true})},result);setExample(id);setPage('studio')}
    catch(e){setError(e instanceof Error?e.message:'Could not run the example')}finally{setBusy(false)}
  }
  async function action(kind:'checkpoint'|'stop'|'review'){
    if(!credentials||!session)return;setBusy(true);setError(null);
    try{if(kind==='stop'){releaseCamera();const result=await api<Session>(`/api/sessions/${credentials.session_id}/stop`,{method:'POST'},credentials);setSession(result)}
      else if(kind==='checkpoint'){const result=await api<Session>(`/api/sessions/${credentials.session_id}/checkpoint`,{method:'POST'},credentials);setSession(result)}
      else{const event=session.unresolved_event_ids[0];if(event){await api(`/api/sessions/${credentials.session_id}/review`,{method:'POST',body:JSON.stringify({event_id:event})},credentials);setNotice('Finding acknowledged. The advisory remains governed by visual evidence.')}}
    }catch(e){setError(e instanceof Error?e.message:'Request failed')}finally{setBusy(false)}
  }
  async function exportReport(format='json'){
    if(!credentials)return;try{await download(`/api/sessions/${credentials.session_id}/report?format=${format}`,`steplock-evidence.${format}`,credentials)}catch(e){setError(e instanceof Error?e.message:'Export failed')}
  }
  async function uploadRecording(){
    if(!file)return;setBusy(true);setError(null);setSelected(null);
    try{if(file.size>50*1024*1024)throw new Error('Use a recording smaller than 50 MiB.');await stopCurrent();const result=await api<Credentials>('/api/sessions',{method:'POST',body:JSON.stringify({recipe_id:recipeKey,source_kind:uploadKind,consent_recorded:uploadConsent})});bind(result);const form=new FormData();form.append('file',file);await api(`/api/sessions/${result.session_id}/upload`,{method:'POST',body:form},result);await api(`/api/sessions/${result.session_id}/start`,{method:'POST',body:JSON.stringify({checkpoint_at_end:false})},result);setUploadModal(false);setPage('studio');setNotice('Recording started. Request the final checkpoint after the replay. Source provenance is user-declared.')}
    catch(e){setError(e instanceof Error?e.message:'Upload failed')}finally{setBusy(false)}
  }
  async function startCamera(){
    if(!consent)return;setBusy(true);setError(null);setSelected(null);
    try{
      await stopCurrent();
      if(cameraMode==='browser'){
        if(!navigator.mediaDevices?.getUserMedia)throw new Error('Camera access is unavailable. Upload a recording instead.');
        stream.current=await navigator.mediaDevices.getUserMedia({video:{width:{ideal:960},height:{ideal:540},facingMode:'environment'},audio:false});
      }
      const result=await api<Credentials>('/api/sessions',{method:'POST',body:JSON.stringify({recipe_id:recipeKey,source_kind:'LIVE_TAGGED',consent_recorded:true,camera_mode:cameraMode,camera_index:cameraIndex})});bind(result);
      await api(`/api/sessions/${result.session_id}/start`,{method:'POST',body:'{}'},result);
      setCameraModal(false);setPage('studio');
      if(cameraMode==='browser'&&video.current&&stream.current){
        video.current.srcObject=stream.current;await video.current.play();cameraActive.current=true;
        const started=performance.now();const canvas=document.createElement('canvas');const context=canvas.getContext('2d')!;
        async function send(){
          if(!cameraActive.current||!video.current)return;
          if(performance.now()-started>120000){releaseCamera();await api(`/api/sessions/${result.session_id}/stop`,{method:'POST'},result);return}
          const width=video.current.videoWidth,height=video.current.videoHeight;const scale=Math.min(1,960/Math.max(width,height));canvas.width=Math.round(width*scale);canvas.height=Math.round(height*scale);
          context.drawImage(video.current,0,0,canvas.width,canvas.height);
          const captured=performance.now()-started;
          const blob=await new Promise<Blob|null>(resolve=>canvas.toBlob(resolve,'image/jpeg',.88));
          if(!blob||!cameraActive.current)return;
          try{const response=await fetch(`${BASE}/api/sessions/${result.session_id}/frame?captured_at_ms=${captured.toFixed(2)}`,{method:'POST',headers:{...authHeaders(result),'Content-Type':'image/jpeg'},body:blob});if(!response.ok)throw new Error('Camera analysis stopped. Upload a recording or start a new session.');if(cameraActive.current)cameraTimer.current=setTimeout(send,200)}
          catch(e){releaseCamera();setError(e instanceof Error?e.message:'Camera connection lost');api(`/api/sessions/${result.session_id}/stop`,{method:'POST'},result).catch(()=>{})}
        }
        send();
      }
    }catch(e){releaseCamera();setError(e instanceof Error?`${e.message} Upload a recording if camera permission is denied.`:'Camera unavailable. Upload a recording instead.')}finally{setBusy(false)}
  }
  function inspect(event:EventRecord){setSelected(event);setPage('evidence')}
  const current=pages.find(p=>p.id===page)!;
  const workspace=useRef<HTMLElement>(null);
  const pageScroll=useRef<HTMLDivElement>(null);
  useEffect(()=>{pageScroll.current?.scrollTo({top:0,left:0,behavior:'instant'})},[page]);
  return <div className="app-shell"><header className="app-header"><a className="brand" href="#" aria-label="STEPLOCK — Procedure studio" onClick={e=>{e.preventDefault();setPage('studio')}}><img className="rq-brand-logo" src={`${import.meta.env.BASE_URL}assets/requiem/steplock-ornate-logo.webp`} alt="STEPLOCK — Visual procedure assurance" width="900" height="450" onError={e=>{e.currentTarget.hidden=true}}/><span className="rq-brand-fallback">STEPLOCK<small>VISUAL PROCEDURE ASSURANCE</small></span></a><nav aria-label="Main navigation">{pages.map(({id,title,icon:Icon})=><button key={id} className={page===id?'active':''} onClick={()=>setPage(id)}><Icon size={15}/>{title}</button>)}</nav><div className="header-status"><span className={apiUp?'connection good':'connection offline'}><i/>{apiUp?'LOCAL ENGINE':'ENGINE OFFLINE'}</span><span className="advisory-tag"><ShieldCheck size={12}/> ADVISORY ONLY</span></div></header>
    <div ref={pageScroll} className="rq-page-scroll" tabIndex={-1} aria-label="Scrollable page"><div className="rq-header-stage"><div className="workspace-title"><div><div className="breadcrumb">WORKBENCH / {page==='studio'?'INSPECTION':page.toUpperCase()} <span>THEME 04 · CYPHER ’26</span></div><h1>{page==='studio'&&<img className="rq-title-art" src={`${import.meta.env.BASE_URL}assets/requiem/procedure-studio-ornate-title.webp`} alt="" aria-hidden="true" width="1100" height="367" onError={e=>{e.currentTarget.hidden=true}}/>}<span className="rq-heading-label">{current.title}<span className="title-period">.</span></span></h1><p>{page==='studio'?'Catch the wrong move before the next step.':page==='evidence'?'Every decision should survive a closer look.':page==='assembly'?'Explore the illustration. Verify against source evidence.':page==='benchmarks'?'Same frames. Measured outcomes. Retained failures.':page==='recipe'?'Make prerequisites explicit. Keep every version traceable.':'A reproducible setup for a marker-assisted demonstration.'}</p></div><div className="title-actions"><button onClick={()=>setPage('kit')}><HelpCircle size={15}/> Setup guide</button>{session&&<button onClick={()=>exportReport('html')}><FileJson size={15}/> HTML report</button>}</div></div></div>
    <main ref={workspace} className="workspace" tabIndex={-1} aria-label="Workspace content">
    {(error||sessionError||!apiUp)&&<div className="error-banner" role="alert"><Activity size={17}/><span>{error||sessionError||'Local engine unavailable. Start the backend or reconnect; a stale decision is never a PASS.'}</span>{error&&<button aria-label="Dismiss error" onClick={()=>setError(null)}><X size={15}/></button>}</div>}
    {notice&&<div className="notice-banner" role="status"><Check size={16}/><span>{notice}</span><button aria-label="Dismiss notification" onClick={()=>setNotice('')}><X size={15}/></button></div>}
    {page==='studio'&&<><section className="source-toolbar" aria-label="Source controls"><div className="recipe-picker"><span className="eyebrow">RECIPE</span><select aria-label="Select recipe" value={recipeKey} onChange={e=>setRecipeKey(e.target.value)}>{recipes.map(r=><option key={r.key} value={r.key}>{r.name} · v{r.version}</option>)}</select></div><div className="source-actions"><select aria-label="Select example" value={example} onChange={e=>setExample(e.target.value)}>{scenarios.map(s=><option key={s.id} value={s.id}>{s.title}</option>)}</select><button className="primary" onClick={()=>runExample()} disabled={busy||!apiUp}>{busy?<Loader2 size={15} className="spin"/>:<Play size={15}/>}Run example</button><span className="toolbar-divider"/><button onClick={()=>setCameraModal(true)} disabled={busy||!apiUp}><Camera size={15}/> Live camera</button><button onClick={()=>setUploadModal(true)} disabled={busy||!apiUp}><Upload size={15}/> Upload</button></div></section><div className="source-hint"><span>Examples: watermarked synthetic footage · final checkpoint included</span><span>{session?`CASE ${session.session_id.slice(0,8).toUpperCase()}`:'NO ACTIVE CASE'} <i/> MARKER-ASSISTED</span></div><Studio session={session} recipe={recipe} credentials={credentials} connected={connected} busy={busy} onCheckpoint={()=>action('checkpoint')} onStop={()=>action('stop')} onReview={()=>action('review')} onEvent={inspect} onExport={()=>exportReport()} onRun={runExample}/></>}
    {page==='evidence'&&<Evidence session={session} credentials={credentials} selected={selected} onSelect={setSelected} onExport={()=>exportReport()}/>}
    {page==='assembly'&&<AssemblyExplorer session={session} recipe={recipe} connected={connected} onEvent={inspect}/>}
    {page==='benchmarks'&&<Benchmarks data={benchmark}/>}
    {page==='recipe'&&<RecipeBuilder recipe={recipe} onSaved={refreshRecipes} onError={setError}/>}
    {page==='kit'&&<GettingStarted/>}
    <footer className="workspace-footer"><span><span className="footer-mark">S</span> SEE THE COMPONENT. KNOW THE STEP. SHOW THE EVIDENCE.</span><span>{health?`OpenCV ${health.cv_version} · CPU`:'Awaiting engine'} <i/> Evidence stored locally</span></footer></main></div>
    <video ref={video} muted playsInline className="capture-element" aria-hidden="true"/>
    {cameraModal&&<div className="modal-backdrop"><section className="modal" role="dialog" aria-modal="true" aria-labelledby="camera-title"><button className="modal-close" aria-label="Close camera setup" onClick={()=>setCameraModal(false)}><X size={20}/></button><Camera size={28} className="accent"/><h2 id="camera-title">Connect your workbench.</h2><p>Frame all four anchors and use harmless tagged parts. No audio is captured. Evidence frames are retained locally for inspection.</p><label className="field-label">Camera connection<select value={cameraMode} onChange={e=>setCameraMode(e.target.value)}><option value="browser">Browser camera (permission prompt)</option><option value="backend">Local OpenCV camera</option></select></label>{cameraMode==='backend'&&<label className="field-label">Camera index<input type="number" min="0" max="8" value={cameraIndex} onChange={e=>setCameraIndex(Number(e.target.value))}/></label>}<label className="consent"><input type="checkbox" checked={consent} onChange={e=>setConsent(e.target.checked)}/><span>I have consent to capture this tabletop, with no faces or sensitive information in view.</span></label><button className="primary" disabled={!consent||busy} onClick={startCamera}>{busy?'Connecting…':'Start consented camera'}<ArrowRight size={15}/></button><button className="text-button" onClick={()=>{setCameraModal(false);setUploadModal(true)}}>Use a recording instead</button></section></div>}
    {uploadModal&&<div className="modal-backdrop"><section className="modal" role="dialog" aria-modal="true" aria-labelledby="upload-title"><button className="modal-close" aria-label="Close upload" onClick={()=>setUploadModal(false)}><X size={20}/></button><Upload size={28} className="accent"/><h2 id="upload-title">Replay a recording.</h2><p>Use consented footage without faces or sensitive audio. Maximum 50 MiB / 2 minutes. Request a final checkpoint after playback.</p><label className="field-label">Source provenance<select value={uploadKind} onChange={e=>setUploadKind(e.target.value as SourceKind)}><option value="REPLAY_TAGGED">Consented recorded camera footage</option><option value="SYNTHETIC_FIXTURE">Generated synthetic test video</option></select></label><label className="upload-drop"><Upload size={24}/><span>{file?.name||'Choose a video file'}</span><small>MP4, AVI, MOV or WebM</small><input aria-label="Choose video recording" type="file" accept="video/*,.avi" onChange={e=>setFile(e.target.files?.[0]||null)}/></label><label className="consent"><input type="checkbox" checked={uploadConsent} onChange={e=>setUploadConsent(e.target.checked)}/><span>I have permission to use this recording and retain its evidence locally.</span></label><button className="primary" disabled={!file||busy||!uploadConsent} onClick={uploadRecording}>{busy?'Uploading & validating…':'Upload & start replay'}<ArrowRight size={15}/></button></section></div>}
  </div>;
}
