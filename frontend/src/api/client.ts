import type {Credentials} from './types';
export const BASE=(import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/,'');
export const authHeaders=(credentials:Credentials|null):Record<string,string>=>credentials?{Authorization:`Bearer ${credentials.access_token}`} : {};
export async function api<T>(path:string, options:RequestInit={}, credentials:Credentials|null=null):Promise<T> {
  const headers=new Headers(options.headers);
  Object.entries(authHeaders(credentials)).forEach(([k,v])=>headers.set(k,v));
  if(options.body && typeof options.body==='string' && !headers.has('Content-Type')) headers.set('Content-Type','application/json');
  const response=await fetch(BASE+path,{...options,headers});
  if(!response.ok){let detail;try{detail=(await response.json()).detail}catch{detail=response.statusText}throw new Error(typeof detail==='string'?detail:JSON.stringify(detail));}
  return response.json() as Promise<T>;
}
export async function download(path:string,name:string,credentials:Credentials){
  const response=await fetch(BASE+path,{headers:authHeaders(credentials)});
  if(!response.ok)throw new Error('Report export failed. Check the connection and try again.');
  const url=URL.createObjectURL(await response.blob());const a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
}
export const clock=(ms:number=0)=>`${Math.floor(ms/60000).toString().padStart(2,'0')}:${(ms/1000%60).toFixed(1).padStart(4,'0')}`;
export const human=(s:string)=>s.replace(/_/g,' ').toLowerCase();
export const percent=(n:number|null|undefined)=>n==null?'—':`${(n*100).toFixed(1)}%`;
export const number=(n:number|null|undefined,digits=1)=>n==null?'—':n.toFixed(digits);
