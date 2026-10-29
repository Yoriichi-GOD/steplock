"""Read-only cadence check. Remote failure is visible, never silently treated as a push."""
import argparse
import datetime as dt
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def git(*args):
    return subprocess.check_output(["git", "-C", str(ROOT), *args], text=True, timeout=20).strip()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit-minutes", type=float, default=40)
    args = parser.parse_args()
    verified = False
    try:
        remote = git("ls-remote", "origin", "refs/heads/main").split()[0]
        timestamp = int(git("show", "-s", "--format=%ct", remote))
        verified = True
    except (subprocess.SubprocessError, IndexError, ValueError):
        remote = git("rev-parse", "HEAD")
        timestamp = int(git("show", "-s", "--format=%ct", remote))
    age = (dt.datetime.now(dt.timezone.utc).timestamp() - timestamp) / 60
    print(f"{'REMOTE_VERIFIED' if verified else 'REMOTE_NOT_VERIFIED'} {remote} age={age:.1f} min")
    return 0 if verified and age <= args.limit_minutes else 1


if __name__ == "__main__":
    sys.exit(main())
