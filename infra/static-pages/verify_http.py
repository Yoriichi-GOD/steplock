"""Verify a published static release over normal DNS and validated HTTPS."""
import argparse
from datetime import datetime,timezone
import hashlib
import json
from email import message_from_bytes
from pathlib import Path
import shutil
import subprocess
import tempfile
from urllib.parse import urlsplit

p=argparse.ArgumentParser()
p.add_argument('origin')
p.add_argument('--output',type=Path,required=True)
a=p.parse_args()
base=a.origin.rstrip('/')
assert urlsplit(base).scheme=='https'
checks=[]
def get(path,headers=None):
    # The public host's Browser Integrity Check rejects urllib (CF error 1010).
    # Use the installed curl HTTP/TLS stack with its unmodified default identity;
    # do not disable that protection, spoof a browser, or bypass TLS validation.
    with tempfile.TemporaryDirectory(prefix='steplock-static-http-') as temp:
        folder=Path(temp)
        command=[shutil.which('curl.exe') or 'curl','--silent','--show-error','--max-time','30','--proto','=https','--dump-header',str(folder/'headers'),'--output',str(folder/'body'),'--write-out','%{http_code}',base+path]
        for key,value in (headers or {}).items():command.extend(['--header',key+': '+value])
        code=int(subprocess.check_output(command,text=True).strip())
        raw=(folder/'headers').read_bytes().split(b'\r\n\r\n')[-2]
        parsed=message_from_bytes(raw.split(b'\r\n',1)[1])
        return code,parsed,(folder/'body').read_bytes(),base+path
for route,status in [('/',200),('/demo',200),('/app',200),('/api/health',404),('/missing-static-route',404)]:
    code,headers,body,url=get(route)
    assert code==status,(route,code)
    assert urlsplit(url).path==route,(route,url)
    assert headers.get('X-Content-Type-Options')=='nosniff'
    assert headers.get('X-Frame-Options')=='DENY'
    assert "camera=()" in headers.get('Permissions-Policy','')
    assert "connect-src 'self'" in headers.get('Content-Security-Policy','')
    if status==200:assert b'type="module"' in body
    checks.append({'route':route,'status':code,'final_url':url,'headers_verified':True})
code,_,body,_=get('/assets/walkthrough/provenance.json')
assert code==200
provenance=json.loads(body)
assert provenance['population']=='SYNTHETIC_FIXTURE'
for clip in provenance['clips']:
    code,headers,body,_=get('/assets/walkthrough/'+clip['name']+'.webm')
    assert code==200 and headers.get_content_type()=='video/webm'
    digest=hashlib.sha256(body).hexdigest()
    assert digest==clip['video_sha256'],clip['name']
    range_code,range_headers,partial,_=get('/assets/walkthrough/'+clip['name']+'.webm',{'Range':'bytes=0-31'})
    # HTTP permits a server to ignore Range and return the complete file. These
    # short clips remain playable after full download; report this limitation.
    assert range_code in (200,206)
    if range_code==206:assert len(partial)==32 and partial==body[:32]
    else:assert partial==body
    caption_code,_,caption,_=get('/assets/walkthrough/'+clip['name']+'.vtt')
    assert caption_code==200 and caption.startswith(b'WEBVTT')
    checks.append({'video':clip['name'],'sha256':digest,'bytes':len(body),'range_status':range_code,'partial_range_supported':range_code==206,'captions':True})
receipt={'result':'PASS','origin':base,'checked_at_utc':datetime.now(timezone.utc).isoformat(),'normal_dns':True,'tls_validation':True,'transport':'Installed curl with default identity; urllib was rejected with CF error 1010. No protection was disabled.','checks':checks,'limits':'Static HTTP delivery and integrity only; browser rendering/playback checked separately. No live inspection or physical accuracy claimed.'}
a.output.parent.mkdir(parents=True,exist_ok=True)
a.output.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
print(json.dumps(receipt))
