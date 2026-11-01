"""Actual HTTP/container smoke: generated pixels through the original engine."""
import argparse
import json
import time
from urllib.request import Request, urlopen
from urllib.error import HTTPError


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--origin", default="http://127.0.0.1:8000")
    args = parser.parse_args()

    def call(path, method="GET", data=None, token=None):
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = "Bearer " + token
        request = Request(args.origin + path, method=method, headers=headers,
                          data=json.dumps(data).encode() if data is not None else None)
        try:
            with urlopen(request, timeout=10) as response:
                raw = response.read()
                return response.status, json.loads(raw) if "json" in response.headers.get("content-type", "") else raw
        except HTTPError as error:
            return error.code, None

    for _ in range(30):
        try:
            if call("/api/health")[0] == 200:
                break
        except OSError:
            pass
        time.sleep(1)
    else:
        raise RuntimeError("Container readiness failed")
    for route in ("/", "/demo", "/app"):
        status, body = call(route)
        assert status == 200 and b'id="root"' in body, route
    for route in ("/api/recipes", "/api/agent/health", "/openapi.json"):
        assert call(route)[0] == 403, route
    results = []
    for scenario, verdict, finding in [("normal", "PASS", "CHECKPOINT"),
            ("wrong_component", "HOLD_FOR_REVIEW", "WRONG_COMPONENT"),
            ("wrong_order", "HOLD_FOR_REVIEW", "ORDER_VIOLATION"),
            ("correction", "PASS", "CORRECTED")]:
        code, created = call("/api/public/demo/sessions", "POST", {"scenario_id": scenario})
        assert code == 201, (scenario, code)
        path = "/api/public/demo/sessions/" + created["session_id"]
        token = created["access_token"]
        assert call(path, token="different-visitor")[0] == 404
        deadline = time.monotonic() + 20
        while time.monotonic() < deadline:
            code, state = call(path, token=token)
            assert code == 200
            if state["state"] != "running":
                break
            time.sleep(.2)
        assert state["state"] == "finished", scenario
        assert state["decision"]["status"] == verdict, state["decision"]
        assert finding in {event["kind"] for event in state["events"]}
        frame = state["latest_frame"]["frame_id"]
        assert call(path + "/frames/" + frame, token=token)[0] == 200
        assert call(path, "DELETE", token=token)[0] == 200
        results.append({"scenario": scenario, "decision": verdict, "finding": finding})
    print(json.dumps({"result": "PASS", "population": "SYNTHETIC_FIXTURE", "provider_calls": 0, "scenarios": results}, indent=2))


if __name__ == "__main__":
    main()
