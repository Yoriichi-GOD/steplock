import {useEffect,useState} from 'react';
import {ScanLine} from 'lucide-react';
import {authHeaders,BASE} from '../api/client';
import type {Credentials} from '../api/types';
export function FrameImage({credentials,frameId,annotated=true,label='Visual evidence',awaitingSource=false}:{credentials:Credentials|null;frameId:string|null|undefined;annotated?:boolean;label?:string;awaitingSource?:boolean}){
  const [url,setUrl]=useState('');const [failed,setFailed]=useState(false);
  useEffect(()=>{
    if(!credentials||!frameId){setUrl('');setFailed(false);return}
    const controller=new AbortController();let disposed=false;let objectUrl='';setFailed(false);
    fetch(`${BASE}/api/sessions/${credentials.session_id}/frames/${frameId}?annotated=${annotated}`,{headers:authHeaders(credentials),signal:controller.signal}).then(r=>{if(!r.ok)throw new Error();return r.blob()}).then(blob=>{objectUrl=URL.createObjectURL(blob);if(!disposed)setUrl(objectUrl)}).catch(()=>{if(!disposed)setFailed(true)});
    return()=>{disposed=true;controller.abort();if(objectUrl)URL.revokeObjectURL(objectUrl)};
  },[credentials,frameId,annotated]);
  return url&&!failed?<img className="evidence-image" src={url} alt={label} onError={()=>setFailed(true)}/>:<div className={`frame-empty ${awaitingSource&&!frameId&&!credentials?'rq-awaiting-source':''}`}>
    {awaitingSource&&!frameId&&!credentials?<img className="rq-flower" src={`${import.meta.env.BASE_URL}assets/requiem/floating-flower.webp`} alt="" aria-hidden="true" width="600" height="400" onError={e=>{e.currentTarget.hidden=true}}/>:<ScanLine size={42}/>}
    <span>{failed?'Evidence unavailable. Reconnect to the local server.':frameId?'Loading evidence…':awaitingSource&&!credentials?'Awaiting an inspection source':'Awaiting source frames'}</span>
    {!frameId&&<small>Run an example, connect a consented camera, or upload a recording.</small>}
  </div>;
}
