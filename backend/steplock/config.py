from pathlib import Path
import os

ROOT = Path(__file__).resolve().parents[2]
RUNTIME = Path(os.environ.get("STEPLOCK_RUNTIME", ROOT / "runtime")).resolve()
MAX_UPLOAD = int(os.environ.get("STEPLOCK_MAX_UPLOAD_MIB", "50")) * 1024 * 1024
MAX_SECONDS = int(os.environ.get("STEPLOCK_MAX_VIDEO_SECONDS", "120"))
