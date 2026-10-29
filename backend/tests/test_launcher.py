"""Exercise the actual launcher against occupied loopback ports."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
import subprocess
import sys
import threading
from contextlib import contextmanager

from steplock.config import ROOT


@contextmanager
def local_server(payload):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-Type","application/json")
            self.end_headers()
            self.wfile.write(json.dumps(payload).encode())

        def log_message(self,*args): pass

    server=ThreadingHTTPServer(("127.0.0.1",0),Handler)
    worker=threading.Thread(target=server.serve_forever,daemon=True)
    worker.start()
    try: yield server.server_port
    finally:
        server.shutdown()
        server.server_close()
        worker.join(timeout=2)


def launch(port):
    return subprocess.run([sys.executable,str(ROOT/"scripts/dev.py"),"--inside-env","--port",str(port)],
                          cwd=ROOT,capture_output=True,text=True,timeout=10,env={**os.environ,"HTTP_PROXY":"http://127.0.0.1:1"})


def test_repeat_launch_reuses_recognized_server_without_proxy_or_new_port():
    with local_server({"status":"ok","advisory_only":True,"aruco_available":True,"cv_version":"test"}) as port:
        result=launch(port)
    assert result.returncode==0,result.stderr
    assert f"already running: http://127.0.0.1:{port}" in result.stdout
    assert "no second server was started" in result.stdout


def test_unrelated_server_is_not_reused_or_replaced_with_random_port():
    with local_server({"status":"ok"}) as port:
        result=launch(port)
    assert result.returncode==1
    assert f"Cannot start STEPLOCK at http://127.0.0.1:{port}" in result.stderr
    assert "no random replacement port" in result.stderr
    assert "STEPLOCK Studio:" not in result.stdout
