import {useEffect,useState} from 'react';
import {api} from '../api/client';
import type {Credentials,Session} from '../api/types';
export function useSession(){
  const [credentials,setCredentials]=useState<Credentials|null>(()=>{try{return JSON.parse(sessionStorage.getItem('steplock-session')||'null')}catch{return null}});
  const [session,setSession]=useState<Session|null>(null);
  const [connected,setConnected]=useState(false);
  const [error,setError]=useState<string|null>(null);
  useEffect(()=>{
    if(!credentials)return;
    let disposed=false;let timer:ReturnType<typeof setTimeout>;
    const controller=new AbortController();
    async function poll(){
      try{const next=await api<Session>(`/api/sessions/${credentials!.session_id}`,{signal:controller.signal},credentials);if(!disposed){setSession(next);setConnected(true);setError(null)}}
      catch(e){if(!disposed){setConnected(false);setError(e instanceof Error?e.message:'Source connection lost')}}
      if(!disposed)timer=setTimeout(poll,300);
    }
    poll();return()=>{disposed=true;controller.abort();clearTimeout(timer)};
  },[credentials]);
  function bind(next:Credentials){sessionStorage.setItem('steplock-session',JSON.stringify(next));setSession(null);setConnected(false);setCredentials(next)}
  return {credentials,session,connected,error,bind,setSession};
}
