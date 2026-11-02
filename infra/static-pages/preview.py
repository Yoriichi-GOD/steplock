"""Local static-only acceptance server; no inspection/backend process."""
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
import json

site=Path(__file__).resolve().parents[2]/'frontend'/'static-dist'
assert (site/'index.html').is_file()
class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(site),**kwargs)
    def do_GET(self):
        if self.path.split('?')[0].rstrip('/') in {'','/demo','/app'}:self.path='/index.html'
        super().do_GET()
    def end_headers(self):
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; font-src 'self'; media-src 'self' blob:; connect-src 'self'; worker-src 'self' blob:; object-src 'none'; base-uri 'self'; frame-ancestors 'none'; form-action 'none'")
        super().end_headers()
    def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
print(json.dumps({'origin':f'http://127.0.0.1:{server.server_port}','backend':False}),flush=True)
server.serve_forever()
