"""Read-only repository/package evidence audit. Does not certify physical safety."""
import bootstrap
import argparse
import json
from pathlib import Path
import subprocess
import sys


def git(*args):
    return subprocess.check_output(["git","-C",str(bootstrap.ROOT),*args],text=True,timeout=30).strip()


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--remote",action="store_true")
    args=parser.parse_args()
    required=["README.md","LICENSE","AGENTS.md","backend/app.py","backend/requirements.lock.txt",
              "frontend/package-lock.json","recipes/tagged_four_part_v1.yaml","demo_kit/printable_board.png",
              "docs/COMPETITION_RULES.md","docs/ARCHITECTURE.md","docs/TECHNICAL_LIMITATIONS.md",
              "docs/EVALUATION_PROTOCOL.md","docs/DATA_SOURCES.md","docs/DEMO_SCRIPT.md",
              "docs/CAPABILITY_TRUTH_TABLE.md","docs/VALIDATION.md"]
    missing=[name for name in required if not (bootstrap.ROOT/name).is_file()]
    tracked=git("ls-files").splitlines()
    forbidden=[name for name in tracked if name.startswith((".venv/","runtime/","node_modules/","data/")) or name==".env" or (name.startswith("fixtures/recorded/") and name not in {"fixtures/recorded/README.md","fixtures/recorded/manifest.csv"})]
    large=[]
    for name in tracked:
        path=bootstrap.ROOT/name
        if path.exists() and path.stat().st_size>20*1024*1024: large.append(name)
    main_head=git("rev-parse","HEAD")
    remote=None
    if args.remote: remote=git("ls-remote","origin","refs/heads/main").split()[0]
    commits=git("log","--reverse","--format=%H|%aI|%s").splitlines()
    result={"head":main_head,"remote":remote,"remote_matches":remote==main_head if remote else None,
            "branch":git("branch","--show-current"),"commit_count":len(commits),"commits":commits,
            "missing_required_files":missing,"forbidden_tracked_paths":forbidden,"tracked_files_over_20mib":large,
            "working_tree":git("status","--short").splitlines(),"physical_capture":"NOT_TESTED",
            "result":"PASS" if not missing and not forbidden and not large and (not args.remote or remote==main_head) else "FAIL"}
    print(json.dumps(result,indent=2))
    return result["result"]!="PASS"


if __name__=="__main__": raise SystemExit(main())
