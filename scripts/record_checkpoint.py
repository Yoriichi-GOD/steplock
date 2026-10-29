"""Record an already completed, remotely verified push. Included in the next commit."""
import argparse
import datetime as dt
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def git(*args):
    return subprocess.check_output(["git", "-C", str(ROOT), *args], text=True, timeout=30).strip()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--milestone", required=True)
    parser.add_argument("--tests", required=True)
    args = parser.parse_args()
    sha = git("rev-parse", "HEAD")
    assert git("ls-remote", "origin", "refs/heads/main").split()[0] == sha, "Remote differs"
    now = dt.datetime.now(dt.timezone.utc)
    india = now.astimezone(dt.timezone(dt.timedelta(hours=5, minutes=30)))
    row = f"| {india.isoformat(timespec='seconds')} | {now.isoformat(timespec='seconds')} | `{sha}` | {args.milestone} | {args.tests} | VERIFIED |\n"
    with (ROOT / "docs/DEVELOPMENT_LOG.md").open("a", encoding="utf-8") as file:
        file.write(row)
    print(row.strip())
