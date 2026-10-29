"""Explicit, idempotent local verification. Never deploys or makes model calls."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--verify',action='store_true');args=parser.parse_args()
    checkpoint=ROOT/'docs/NVIDIA_NEBIUS_CHECKPOINT.json'
    print(checkpoint.read_text() if checkpoint.exists() else 'Read docs/NVIDIA_NEBIUS_PROGRESS.md; no checkpoint JSON yet.')
    if not args.verify:return
    npm='npm.cmd' if os.name=='nt' else 'npm'
    commands=[[sys.executable,'-m','pytest','backend/tests','-q'],[npm,'--prefix','frontend','test'],[npm,'--prefix','frontend','run','build']]
    for command in commands:
        completed=subprocess.run(command,cwd=ROOT)
        if completed.returncode:raise SystemExit(completed.returncode)
    print(json.dumps({'local_verification':'PASS','cloud_calls':0,'resources_created':0,'submission_performed':False}))


if __name__=='__main__':main()
