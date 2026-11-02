import {execFileSync} from 'node:child_process';
import {cpSync,existsSync,readdirSync,statSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import path from 'node:path';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const output=path.join(root,'frontend/static-dist');
for(const name of ['normal','wrong-component','correction']){
  if(!existsSync(path.join(root,'frontend/public/assets/walkthrough',name+'.webm')))throw new Error('Missing verified recording: '+name);
}
execFileSync(process.execPath,[path.join(root,'frontend/node_modules/typescript/bin/tsc'),'-b'],{cwd:path.join(root,'frontend'),stdio:'inherit'});
execFileSync(process.execPath,[path.join(root,'frontend/node_modules/vite/bin/vite.js'),'build','--outDir','static-dist'],{cwd:path.join(root,'frontend'),stdio:'inherit',env:{...process.env,VITE_PUBLIC_PRESENTATION:'recorded',VITE_API_BASE_URL:''}});
cpSync(path.join(root,'infra/static-pages/public'),output,{recursive:true});
// Native extensionless Pages routes avoid proxying /index.html, whose canonical
// redirect would send /demo back to /. Keep the explicit top-level 404 for /api.
for(const route of ['demo','app'])cpSync(path.join(output,'index.html'),path.join(output,route+'.html'));
const files=[];
function walk(dir){for(const name of readdirSync(dir)){const file=path.join(dir,name);if(statSync(file).isDirectory())walk(file);else files.push({file:path.relative(output,file),bytes:statSync(file).size});}}
walk(output);
if(files.length>20000||files.some(f=>f.bytes>25*1024*1024))throw new Error('Cloudflare Pages Free asset limits exceeded');
if(files.some(f=>f.file==='_worker.js'||f.file.startsWith('functions/')))throw new Error('This release must contain static assets only');
console.log(JSON.stringify({output,files:files.length,largest:Math.max(...files.map(f=>f.bytes)),backend:false,functions:false}));
