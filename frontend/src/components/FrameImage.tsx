import {useEffect,useState} from 'react';
import {ScanLine} from 'lucide-react';
import {authHeaders,BASE} from '../api/client';
import type {Credentials} from '../api/types';
export function FrameImage({credentials,frameId,annotated=true,label='Visual evidence'}:{credentials:Credentials|null;frameId:string|null|undefined;annotated?:boolean;label?:string}){
  const [url,setUrl]=useState('');const [failed,setFailed]=useState(false);
  useEffect(()=>{
    if(!credentials||!frameId){setUrl('');return}
    const controller=new AbortController();let disposed=false;let objectUrl='';setFailed(false);
    fetch(`${BASE}/api/sessions/${credentials.session_id}/frames/${frameId}?annotated=${annotated}`,{headers:authHeaders(credentials),signal:controller.signal}).then(r=>{if(!r.ok)throw new Error();return r.blob()}).then(blob=>{objectUrl=URL.createObjectURL(blob);if(!disposed)setUrl(objectUrl)}).catch(()=>{if(!disposed)setFailed(true)});
    return()=>{disposed=true;controller.abort();if(objectUrl)URL.revokeObjectURL(objectUrl)};
  },[credentials,frameId,annotated]);
  return url&&!failed?<img className="evidence-image" src={url} alt={label}/>:<div className="frame-empty"><ScanLine size={42}/><span>{failed?'Evidence unavailable. Reconnect to the local server.':frameId?'Loading evidence…':'Your workbench, verified.'}</span>{!frameId&&<small>Run an example or connect a consented camera.</small>}</div>;
}
