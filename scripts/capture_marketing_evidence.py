"""Capture a genuine generated-example result for a clearly labeled retained case.

Uses the restricted API, not annotations. No access token is written to disk.
"""
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import time
from urllib.request import Request, ProxyHandler, build_opener


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--origin", default="http://127.0.0.1:62401")
    args = parser.parse_args()
    opener = build_opener(ProxyHandler({}))
    token = None

    def call(path, method="GET", body=None, binary=False):
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = "Bearer " + token
        request = Request(args.origin + path, method=method, headers=headers,
                          data=json.dumps(body).encode() if body is not None else None)
        with opener.open(request, timeout=15) as response:
            data = response.read()
            return data if binary else json.loads(data)

    created = call("/api/public/demo/sessions", "POST", {"scenario_id": "wrong_component"})
    token = created["access_token"]
    path = "/api/public/demo/sessions/" + created["session_id"]
    try:
        deadline = time.monotonic() + 25
        while time.monotonic() < deadline:
            state = call(path)
            if state["state"] != "running":
                break
            time.sleep(.2)
        assert state["state"] == "finished" and state["decision"]["status"] == "HOLD_FOR_REVIEW"
        finding = next(event for event in state["events"] if event["kind"] == "WRONG_COMPONENT")
        dest = Path(__file__).resolve().parents[1] / "frontend/public/assets/industrial"
        dest.mkdir(parents=True, exist_ok=True)
        files = []
        for annotated, name in [(False, "source.png"), (True, "overlay.jpg")]:
            data = call(path + "/frames/" + finding["frame_id"] + "?annotated=" + str(annotated).lower(), binary=True)
            (dest / name).write_bytes(data)
            files.append({"file": name, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
        receipt = {"capture_kind": "RETAINED_ENGINE_RESULT", "population": "SYNTHETIC_FIXTURE",
                   "captured_at": dt.datetime.now(dt.timezone.utc).isoformat(),
                   "notice": "Actual engine result on generated software test pixels. Retained example, not live factory footage.",
                   "recipe_sha256": state["recipe_sha256"], "source_sha256": state["source_sha256"],
                   "decision": state["decision"], "finding": finding, "files": files}
        (dest / "evidence-case.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"result": "PASS", "files": files, "event": finding["kind"]}))
    finally:
        call(path, "DELETE")


if __name__ == "__main__":
    main()
