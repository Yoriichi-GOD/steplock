import json
import os
import time
import pytest
from fastapi.testclient import TestClient
from backend.app import create_app


@pytest.fixture
def public(tmp_path, monkeypatch):
    monkeypatch.setenv("STEPLOCK_PUBLIC_MODE", "1")
    monkeypatch.setenv("STEPLOCK_OWNER_KEY", "owner-key-for-tests-" * 3)
    monkeypatch.setenv("STEPLOCK_TRUSTED_HOSTS", "testserver,localhost")
    with TestClient(create_app(tmp_path)) as client:
        yield client


def start(client, scenario="normal"):
    response = client.post("/api/public/demo/sessions", json={"scenario_id": scenario})
    assert response.status_code == 201, response.text
    data = response.json()
    return data["session_id"], {"Authorization": "Bearer " + data["access_token"]}


def finish(client, sid, headers):
    end = time.monotonic() + 15
    while time.monotonic() < end:
        response = client.get(f"/api/public/demo/sessions/{sid}", headers=headers)
        assert response.status_code == 200
        data = response.json()
        if data["state"] != "running":
            return data
        time.sleep(.1)
    pytest.fail("Real replay did not finish")


def test_public_boundary_restricts_old_routes_even_when_controls_are_hidden(public):
    for method, path in [("get", "/api/recipes"), ("post", "/api/recipes"), ("post", "/api/sessions"),
                         ("post", "/api/sessions/foreign/frame"), ("post", "/api/sessions/foreign/upload"),
                         ("post", "/api/sessions/foreign/agent/explain"), ("get", "/api/agent/health"),
                         ("get", "/api/benchmarks/latest"), ("get", "/openapi.json"), ("get", "/docs")]:
        assert getattr(public, method)(path).status_code == 403, path
    health = public.get("/api/health")
    assert health.status_code == 200
    assert "active_session_id" not in health.json()
    assert health.headers["permissions-policy"] == "camera=(), microphone=()"


def test_only_approved_files_and_bounded_requests(public):
    data = public.get("/api/public/demo/scenarios").json()
    assert [r["id"] for r in data["scenarios"]] == ["normal", "wrong_component", "wrong_order", "correction"]
    assert all(r["available"] for r in data["scenarios"])
    assert "relative_path" not in json.dumps(data)
    for body in [{"scenario_id": "../../private"}, {"scenario_id": "physical_recording"},
                 {"scenario_id": "normal", "source_kind": "LIVE_TAGGED"}]:
        assert public.post("/api/public/demo/sessions", json=body).status_code == 422
    assert public.post("/api/public/demo/sessions", content=b"x" * 2049).status_code == 413
    assert public.post("/api/public/demo/sessions", content=iter([b"a" * 1024] * 3)).status_code == 413
    assert public.post("/api/public/demo/sessions", json={"scenario_id": "normal"}, headers={"Origin": "https://foreign.example"}).status_code == 403


def test_real_public_replays_and_retained_correction(public):
    for scenario, expected_event, expected_verdict in [("normal", "CHECKPOINT", "PASS"),
            ("wrong_component", "WRONG_COMPONENT", "HOLD_FOR_REVIEW"), ("wrong_order", "ORDER_VIOLATION", "HOLD_FOR_REVIEW"),
            ("correction", "CORRECTED", "PASS")]:
        sid, headers = start(public, scenario)
        assert public.get(f"/api/public/demo/sessions/{sid}", headers={"Authorization": "Bearer foreign"}).status_code == 404
        assert public.post("/api/public/demo/sessions", json={"scenario_id": "normal"}).status_code == 409
        data = finish(public, sid, headers)
        assert data["decision"]["status"] == expected_verdict, data["decision"]
        assert expected_event in {e["kind"] for e in data["events"]}
        if scenario == "correction":
            corrected = next(e for e in data["events"] if e["kind"] == "CORRECTED")
            assert corrected["resolves_event_id"] in {e["event_id"] for e in data["events"] if e["kind"] == "WRONG_COMPONENT"}
        frame = data["latest_frame"]["frame_id"]
        for annotated in ("true", "false"):
            response = public.get(f"/api/public/demo/sessions/{sid}/frames/{frame}?annotated={annotated}", headers=headers)
            assert response.status_code == 200 and len(response.content) > 100
            assert response.headers["content-type"] == ("image/jpeg" if annotated == "true" else "image/png")
            assert response.headers["cache-control"] == "no-store"
        directory = public.app.state.public_demo.manager.sessions[sid].directory
        assert public.delete(f"/api/public/demo/sessions/{sid}", headers=headers).status_code == 200
        assert not directory.exists()
        assert public.get(f"/api/public/demo/sessions/{sid}", headers=headers).status_code == 404


def test_rate_limits_persist_across_recreated_gateway(public):
    demo = public.app.state.public_demo
    for _ in range(16):
        public.post("/api/public/demo/sessions", json={"scenario_id": "invalid"})
    response = public.post("/api/public/demo/sessions", json={"scenario_id": "normal"})
    assert response.status_code == 429 and "retry-after" in response.headers
    replacement = create_app(demo.root.parent)
    with TestClient(replacement) as second:
        assert second.post("/api/public/demo/sessions", json={"scenario_id": "normal"}).status_code == 429


def test_owner_login_and_expiry(public):
    assert public.post("/api/owner/login", json={"key": "wrong"}).status_code == 403
    assert public.post("/api/owner/login", json={"key": "owner-key-for-tests-" * 3}).status_code == 200
    assert public.get("/api/recipes").status_code == 200
    assert public.get("/api/public/config").json()["owner_authenticated"] is True
    public.post("/api/owner/logout")
    assert public.get("/api/recipes").status_code == 403
    sid, headers = start(public)
    demo = public.app.state.public_demo
    demo.created[sid] -= demo.ttl_seconds + 1
    assert public.get(f"/api/public/demo/sessions/{sid}", headers=headers).status_code == 404


def test_missing_contact_is_honest_and_tokens_do_not_appear_in_config(public, monkeypatch):
    monkeypatch.setenv("STEPLOCK_PUBLIC_CONTACT", "placeholder")
    response = public.get("/api/public/config")
    assert response.json()["contact_email"] is None
    assert "owner-key-for-tests" not in response.text


def test_health_target_host_exception_is_narrow_and_tls_cookie_is_secure(public):
    assert public.get("/api/health", headers={"Host": "10.20.30.40:8000"}).status_code == 200
    assert public.post("/api/health", headers={"Host": "10.20.30.40:8000"}).status_code == 400
    assert public.get("/api/public/config", headers={"Host": "foreign.example"}).status_code == 400
    with TestClient(public.app, base_url="https://localhost") as secure:
        response = secure.post("/api/owner/login", json={"key": "owner-key-for-tests-" * 3})
        cookie = response.headers["set-cookie"].lower()
        assert "secure" in cookie and "httponly" in cookie and "samesite=strict" in cookie
        assert response.headers["strict-transport-security"] == "max-age=86400"
        assert "frame-ancestors 'none'" in response.headers["content-security-policy"]
        assert secure.get("/api/recipes").status_code == 200


def test_retention_capacity_and_restart_orphan_cleanup(public):
    demo = public.app.state.public_demo
    demo.maximum_sessions = 1
    sid, headers = start(public)
    state = finish(public, sid, headers)
    assert public.post("/api/public/demo/sessions", json={"scenario_id": "normal"}).status_code == 429
    frame = state["latest_frame"]["frame_id"]
    demo.created[sid] -= demo.ttl_seconds + 1
    assert public.get(f"/api/public/demo/sessions/{sid}/frames/{frame}", headers=headers).status_code == 404
    assert not (demo.root / "sessions" / sid).exists()
    orphan = demo.root / "sessions" / ("a" * 32)
    orphan.mkdir()
    (orphan / "evidence.txt").write_text("expired public evidence")
    os.utime(orphan, (time.time() - 700, time.time() - 700))
    unrelated = demo.root / "sessions" / "keep-me"
    unrelated.mkdir()
    demo.cleanup()
    assert not orphan.exists()
    assert unrelated.is_dir()
