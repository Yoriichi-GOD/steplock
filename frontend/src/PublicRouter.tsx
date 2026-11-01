import {lazy,Suspense,useEffect,useState} from 'react';
import {api} from './api/client';
import type {PublicConfig} from './components/marketing/PublicChrome';

const Landing=lazy(()=>import('./pages/LandingPage'));
const Demo=lazy(()=>import('./pages/PublicDemo'));
const Workspace=lazy(()=>import('./App'));

function WorkspaceGate(){
  const [config,setConfig]=useState<PublicConfig|null>(null);const [error,setError]=useState('');const [key,setKey]=useState('');const [busy,setBusy]=useState(false);
  useEffect(()=>{const controller=new AbortController();api<PublicConfig>('/api/public/config',{signal:controller.signal}).then(setConfig).catch(()=>setError('Workspace connection unavailable. Reconnect before continuing.'));return()=>controller.abort()},[]);
  if(config&&(!config.public_mode||config.owner_authenticated))return <Workspace/>;
  return <main className="public-page gate-page"><a className="wordmark" href="/">STEPLOCK<span> / PRIVATE WORKSPACE</span></a><div><span className="kicker">OWNER ACCESS</span><h1>The full workbench.</h1><p>The public demo runs prepared examples. Camera capture, uploads and recipe editing belong in the restricted workspace.</p>{config?.owner_access_enabled?<form onSubmit={async e=>{e.preventDefault();setBusy(true);setError('');try{await api('/api/owner/login',{method:'POST',body:JSON.stringify({key})});setKey('');setConfig(await api('/api/public/config'))}catch(e){setError(e instanceof Error?e.message:'Could not sign in')}finally{setBusy(false)}}}><label>Owner access key<input type="password" autoComplete="current-password" value={key} onChange={e=>setKey(e.target.value)} required/></label><button className="button-gold" disabled={busy}>{busy?'Checking access…':'Open workspace'}</button></form>:<p className="notice">{config?'Owner access is not configured on this deployment. The full workspace remains available in the local installation.':'Checking workspace availability…'}</p>}{error&&<p role="alert">{error}</p>}<a className="button-outline" href="/demo">Try the public demo ↗</a></div></main>;
}

const routes:Record<string,()=>React.ReactNode>={'/':()=> <Landing/>,'/demo':()=> <Demo/>,'/app':()=> <WorkspaceGate/>};
export function PublicRouter(){const path=window.location.pathname.replace(/\/$/,'')||'/';const route=routes[path];return <Suspense fallback={<main className="public-page route-loading" role="status">STEPLOCK / Loading the workbench…</main>}>{route?route():<main className="public-page gate-page"><h1>That page isn’t here.</h1><a href="/">Return to STEPLOCK</a></main>}</Suspense>}
