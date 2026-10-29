"""One-command local setup/launch. Reserves a free loopback socket without a port race."""
import argparse
import os
from pathlib import Path
import socket
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--setup",action="store_true",help="Create isolated environment, install dependencies and build the frontend")
    parser.add_argument("--port",type=int,default=int(os.environ.get("STEPLOCK_PORT","0")))
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
        if not (ROOT/"frontend/node_modules").exists(): subprocess.run([npm,"ci","--no-audit","--no-fund"],cwd=ROOT/"frontend",check=True)
        subprocess.run([npm,"run","build"],cwd=ROOT/"frontend",check=True)
    if not (ROOT/"frontend/dist/index.html").exists(): parser.error("Frontend build missing. Run with --setup, or npm run build in frontend")
    sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/"backend"))
    import uvicorn
    from backend.app import app
    listener=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    try:
        listener.bind((args.host,args.port));listener.listen(128)
        actual=listener.getsockname()[1]
        print(f"\nSTEPLOCK Studio: http://127.0.0.1:{actual}\nAPI health: http://127.0.0.1:{actual}/api/health\nLoopback only. No camera starts automatically. Ctrl+C stops this server.\n",flush=True)
        uvicorn.Server(uvicorn.Config(app,host=args.host,port=actual,log_level="info")).run(sockets=[listener])
    finally: listener.close()
    return 0


if __name__=="__main__":
    raise SystemExit(main())
