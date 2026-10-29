"""One-command local setup/launch at a stable loopback address."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
from urllib.request import ProxyHandler, build_opener
import webbrowser

ROOT=Path(__file__).resolve().parents[1]
DEFAULT_PORT=62327


def existing_studio(url):
    """Recognize our local API without using proxy settings or stopping processes."""
    try:
        with build_opener(ProxyHandler({})).open(f"{url}/api/health",timeout=2) as response:
            data=json.load(response)
        return isinstance(data,dict) and data.get("status")=="ok" and data.get("advisory_only") is True and "aruco_available" in data and "cv_version" in data
    except (OSError,ValueError):
        return False


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--setup",action="store_true",help="Create isolated environment, install dependencies and build the frontend")
    parser.add_argument("--port",type=int,default=int(os.environ.get("STEPLOCK_PORT",str(DEFAULT_PORT))),help=f"Stable default: {DEFAULT_PORT}. Use 0 only for an explicit temporary test server.")
    parser.add_argument("--open",action="store_true",help="Open the stable local address in your default browser")
    parser.add_argument("--host",default=os.environ.get("STEPLOCK_HOST","127.0.0.1"))
    parser.add_argument("--inside-env",action="store_true",help=argparse.SUPPRESS)
    args=parser.parse_args()
    if args.host not in {"127.0.0.1","localhost"}: parser.error("This demonstration launcher binds only to loopback")
    if not 0<=args.port<=65535: parser.error("Port must be 0 (auto) or 1–65535")
    os.chdir(ROOT)
    executable=ROOT/".venv"/("Scripts/python.exe" if os.name=="nt" else "bin/python")
    if not executable.exists():
        if not args.setup: parser.error("Run python scripts/dev.py --setup for the first launch")
        subprocess.run([sys.executable,"-m","venv",str(ROOT/".venv")],check=True)
    if not args.inside_env and Path(sys.executable).absolute()!=executable.absolute():
        command=[str(executable),str(Path(__file__).resolve()),*sys.argv[1:],"--inside-env"]
        return subprocess.call(command)
    if args.setup:
        subprocess.run([sys.executable,"-m","pip","install","--disable-pip-version-check","-r","backend/requirements.lock.txt"],check=True)
        npm="npm.cmd" if os.name=="nt" else "npm"
        lock_hash=hashlib.sha256((ROOT/"frontend/package-lock.json").read_bytes()).hexdigest()
        stamp=ROOT/"frontend/node_modules/.steplock-lock"
        if not stamp.exists() or stamp.read_text(encoding="utf-8")!=lock_hash:
            subprocess.run([npm,"ci","--no-audit","--no-fund"],cwd=ROOT/"frontend",check=True)
            stamp.write_text(lock_hash,encoding="utf-8")
        subprocess.run([npm,"run","build"],cwd=ROOT/"frontend",check=True)
    if not (ROOT/"frontend/dist/index.html").exists(): parser.error("Frontend build missing. Run with --setup, or npm run build in frontend")
    listener=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    try:
        try:
            listener.bind((args.host,args.port))
        except OSError as exc:
            url=f"http://127.0.0.1:{args.port}"
            if args.port and existing_studio(url):
                print(f"STEPLOCK is already running: {url}\nReusing the existing server; no second server was started.",flush=True)
                if args.open: webbrowser.open(url)
                return 0
            parser.exit(1,f"Cannot start STEPLOCK at {url}: {exc}\nThe address stays fixed; no random replacement port was selected. Close the conflicting app, then launch again.\n")
        listener.listen(128)
        actual=listener.getsockname()[1]
        print(f"\nSTEPLOCK Studio: http://127.0.0.1:{actual}\nAPI health: http://127.0.0.1:{actual}/api/health\nLoopback only. No camera starts automatically. Ctrl+C stops this server.\n",flush=True)
        sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/"backend"))
        import uvicorn
        from backend.app import app
        if args.open: webbrowser.open(f"http://127.0.0.1:{actual}")
        uvicorn.Server(uvicorn.Config(app,host=args.host,port=actual,log_level="info",access_log=False)).run(sockets=[listener])
    finally: listener.close()
    return 0


if __name__=="__main__":
    raise SystemExit(main())
