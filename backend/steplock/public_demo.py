"""Restricted generated-example gateway. Never reads evaluator ground truth."""
from contextlib import contextmanager
import hashlib
import hmac
import json
import os
from pathlib import Path
import re
import secrets
import shutil
import sqlite3
import threading
import time

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import Response, JSONResponse
from pydantic import BaseModel, ConfigDict
from starlette.middleware.trustedhost import TrustedHostMiddleware

from .config import ROOT
from .service import Session, SessionManager
from .sources.replay import inspect_video

APPROVED = ("normal", "wrong_component", "wrong_order", "correction")


class PublicTrustedHosts(TrustedHostMiddleware):
    def __init__(self, app, allowed_hosts, health_passthrough=False):
        super().__init__(app, allowed_hosts=allowed_hosts)
        self.health_passthrough = health_passthrough

    async def __call__(self, scope, receive, send):
        # ALB target checks use the target's private IP as Host. Only this fixed,
        # read-only, non-session readiness endpoint may bypass hostname matching.
        if self.health_passthrough and scope["type"] == "http" and scope["method"] == "GET" and scope["path"] == "/api/health":
            return await self.app(scope, receive, send)
        return await super().__call__(scope, receive, send)


class DemoRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    scenario_id: str


class OwnerRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    key: str


class PublicBodyLimit:
    """Bound anonymous JSON before FastAPI/Pydantic parses it, including chunked bodies."""
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or scope["method"] != "POST" or not scope["path"].startswith(("/api/public/", "/api/owner/")):
            return await self.app(scope, receive, send)
        body = bytearray()
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                return
            body.extend(message.get("body", b""))
            if len(body) > 2048:
                return await JSONResponse({"detail": "Request exceeds 2 KiB"}, status_code=413)(scope, receive, send)
            if not message.get("more_body", False):
                break
        delivered = False

        async def bounded_receive():
            nonlocal delivered
            if not delivered:
                delivered = True
                return {"type": "http.request", "body": bytes(body), "more_body": False}
            return await receive()

        return await self.app(scope, bounded_receive, send)


class PublicDemo:
    ttl_seconds = 600
    maximum_sessions = 12
    maximum_run_seconds = 25

    def __init__(self, runtime, recipe, public_mode=False):
        self.root = (Path(runtime) / "public_demo").resolve()
        self.recipe = recipe
        self.public_mode = public_mode
        self.manager = SessionManager()
        self.lock = threading.RLock()
        self.created = {}
        self.started = {}
        self.closed = threading.Event()
        self.owner_key = os.environ.get("STEPLOCK_OWNER_KEY", "")
        self.secret = None
        self.router = APIRouter()
        self._routes()

    @contextmanager
    def database(self):
        self.root.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.root / "limits.sqlite3", timeout=5)
        try:
            connection.execute("PRAGMA busy_timeout=5000")
            connection.execute("CREATE TABLE IF NOT EXISTS counters (key TEXT PRIMARY KEY, started REAL NOT NULL, count INTEGER NOT NULL)")
            connection.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
            connection.execute("INSERT OR IGNORE INTO settings VALUES ('secret', ?)", (secrets.token_hex(32),))
            connection.commit()
            yield connection
        finally:
            connection.close()

    def _secret(self):
        if self.secret is None:
            with self.database() as db:
                self.secret = db.execute("SELECT value FROM settings WHERE key='secret'").fetchone()[0].encode()
        return self.secret

    def rate_limit(self, request, kind="start"):
        # Use the actual peer as interpreted by a narrowly trusted deployment proxy.
        # Never interpret caller-supplied X-Forwarded-For here.
        peer = request.client.host if request.client else "unknown"
        digest = hmac.new(self._secret(), peer.encode(), hashlib.sha256).hexdigest()
        window, maximum = (900, 5) if kind == "login" else (3600, 16)
        now = time.time()
        with self.database() as db:
            db.execute("BEGIN IMMEDIATE")
            db.execute("DELETE FROM counters WHERE started < ?", (now - 3600,))
            for key, limit in ((kind + ":" + digest, maximum), (kind + ":global", maximum * 4)):
                row = db.execute("SELECT started,count FROM counters WHERE key=?", (key,)).fetchone()
                if row and now - row[0] < window and row[1] >= limit:
                    raise HTTPException(429, "Demo request limit reached. Please try later.", headers={"Retry-After": str(max(1, int(window - (now - row[0]))))})
                count, began = (row[1] + 1, row[0]) if row and now - row[0] < window else (1, now)
                db.execute("INSERT OR REPLACE INTO counters VALUES (?,?,?)", (key, began, count))
            db.commit()

    def owner_authorized(self, request):
        cookie = request.cookies.get("steplock_owner", "")
        try:
            expires, signature = cookie.split(".", 1)
            if not self.owner_key or len(self.owner_key) < 32 or not time.time() < int(expires) <= time.time() + 3700:
                return False
            expected = hmac.new(self.owner_key.encode(), expires.encode(), hashlib.sha256).hexdigest()
            return hmac.compare_digest(signature, expected)
        except (ValueError, TypeError):
            return False

    def scenarios(self):
        catalog = json.loads((ROOT / "fixtures/synthetic/catalog.json").read_text(encoding="utf-8"))
        result = []
        for identifier in APPROVED:
            row = next((r for r in catalog if r["id"] == identifier), None)
            if row is None:
                continue
            path = (ROOT / row["relative_path"]).resolve()
            valid = path.is_relative_to(ROOT / "fixtures/synthetic") and path.is_file()
            if valid:
                valid = hashlib.sha256(path.read_bytes()).hexdigest() == row["source_sha256"]
            result.append({**{k: row[k] for k in ("id", "title", "source_kind", "source_sha256", "duration_ms")}, "available": valid})
        return result

    def cleanup(self):
        with self.lock:
            now = time.monotonic()
            for sid, began in list(self.created.items()):
                session = self.manager.sessions[sid]
                if sid in self.started and session.state == "running" and now - self.started[sid] > self.maximum_run_seconds:
                    session.stop()
                if now - began > self.ttl_seconds:
                    self.remove(sid)
            directory = self.root / "sessions"
            if directory.is_dir():
                for orphan in directory.iterdir():
                    if orphan.name not in self.manager.sessions and re.fullmatch(r"[a-f0-9]{32}", orphan.name) and orphan.is_dir() and not orphan.is_symlink():
                        if orphan.resolve().parent == directory and time.time() - orphan.stat().st_mtime > self.ttl_seconds:
                            shutil.rmtree(orphan)

    def remove(self, sid):
        session = self.manager.sessions.get(sid)
        if session is None:
            return
        session.stop()
        if any(t.is_alive() for t in session.threads):
            raise HTTPException(409, "Inspection is stopping; please retry shortly.")
        self.manager.release(sid)
        directory = session.directory.resolve()
        if not re.fullmatch(r"[a-f0-9]{32}", sid) or directory != self.root / "sessions" / sid:
            raise RuntimeError("Invalid demo cleanup boundary")
        if directory.exists():
            shutil.rmtree(directory)
        del self.manager.sessions[sid]
        self.created.pop(sid, None)
        self.started.pop(sid, None)

    def get(self, sid, request):
        self.cleanup()
        with self.lock:
            session = self.manager.sessions.get(sid)
            supplied = request.headers.get("authorization", "").removeprefix("Bearer ")
            if session is None or not hmac.compare_digest(supplied, session.token):
                raise HTTPException(404, "Demo session is unavailable or expired. Run a new inspection.")
            return session

    def snapshot(self, session):
        result = session.snapshot()
        result["error"] = "Inspection could not complete. Start a new example." if result["error"] else None
        result["source_metadata"] = {"population": "SYNTHETIC_FIXTURE", "notice": "Generated software test, not physical camera footage."}
        result["expires_in_seconds"] = max(0, int(self.ttl_seconds - (time.monotonic() - self.created[session.id])))
        return result

    def start_cleanup(self):
        def loop():
            while not self.closed.wait(5):
                try:
                    self.cleanup()
                except (OSError, HTTPException):
                    pass  # A retryable stop/cleanup failure never deletes a live session.
        self.thread = threading.Thread(target=loop, name="public-demo-cleanup", daemon=True)
        self.thread.start()

    def close(self):
        self.closed.set()
        if hasattr(self, "thread"):
            self.thread.join(timeout=6)
        self.manager.stop_all()

    def _routes(self):
        router = self.router

        @router.get("/api/public/config")
        def config(request: Request):
            contact = os.environ.get("STEPLOCK_PUBLIC_CONTACT", "")
            if not re.fullmatch(r"[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", contact):
                contact = None
            return {"public_mode": self.public_mode, "contact_email": contact,
                    "owner_access_enabled": len(self.owner_key) >= 32, "owner_authenticated": self.owner_authorized(request),
                    "demo_population": "SYNTHETIC_FIXTURE", "demo_ttl_seconds": self.ttl_seconds}

        @router.post("/api/owner/login")
        def login(data: OwnerRequest, request: Request):
            self.rate_limit(request, "login")
            if len(self.owner_key) < 32 or not secrets.compare_digest(data.key, self.owner_key):
                raise HTTPException(403, "Owner access is unavailable or the key is incorrect.")
            expires = str(int(time.time() + 3600))
            signature = hmac.new(self.owner_key.encode(), expires.encode(), hashlib.sha256).hexdigest()
            response = JSONResponse({"authorized": True})
            response.set_cookie("steplock_owner", expires + "." + signature, max_age=3600, httponly=True,
                                secure=request.url.scheme == "https", samesite="strict")
            response.headers["Cache-Control"] = "no-store"
            return response

        @router.post("/api/owner/logout")
        def logout():
            response = JSONResponse({"authorized": False})
            response.delete_cookie("steplock_owner")
            return response

        @router.get("/api/public/demo/scenarios")
        def scenarios():
            return {"scenarios": self.scenarios(), "notice": "Actual engine processing generated example pixels. Advisory only."}

        @router.post("/api/public/demo/sessions", status_code=201)
        def create(data: DemoRequest, request: Request):
            self.rate_limit(request)
            self.cleanup()
            with self.lock:
                if len(self.manager.sessions) >= self.maximum_sessions:
                    raise HTTPException(429, "Demo capacity reached. Reset your previous inspection or try later.", headers={"Retry-After": "60"})
                active = self.manager.sessions.get(self.manager.active_id)
                if active and active.state in {"running", "stopping"}:
                    raise HTTPException(409, "Another visitor is running an inspection. Please retry in a few seconds.")
                row = next((r for r in self.scenarios() if r["id"] == data.scenario_id and r["available"]), None)
                if row is None:
                    raise HTTPException(422, "This example is unavailable. Choose an approved scenario.")
                path = ROOT / f"fixtures/synthetic/{dict(zip(APPROVED, ('fx_00_00.avi','fx_01_00.avi','fx_03_00.avi','fx_05_00.avi')))[data.scenario_id]}"
                session = Session(self.recipe, "SYNTHETIC_FIXTURE", False, inspect_video(path))
                session.directory = self.root / "sessions" / session.id
                session.path = path
                self.manager.sessions[session.id] = session
                self.created[session.id] = time.monotonic()
                self.started[session.id] = time.monotonic()
                try:
                    self.manager.start(session, auto_checkpoint=True)
                except Exception:
                    self.remove(session.id)
                    raise HTTPException(503, "Inspection could not start. Please try again.")
                return {"session_id": session.id, "access_token": session.token, "snapshot": self.snapshot(session)}

        @router.get("/api/public/demo/sessions/{sid}")
        def snapshot(sid: str, request: Request):
            with self.lock:
                return self.snapshot(self.get(sid, request))

        @router.delete("/api/public/demo/sessions/{sid}")
        def remove(sid: str, request: Request):
            with self.lock:
                self.get(sid, request)
                self.remove(sid)
            return {"removed": True}

        @router.get("/api/public/demo/sessions/{sid}/frames/{frame_id}")
        def frame(sid: str, frame_id: str, request: Request, annotated: bool = True):
            # Copy one bounded evidence frame while cleanup is excluded. A deferred
            # FileResponse could otherwise open a file after its TTL cleanup.
            with self.lock:
                session = self.get(sid, request)
                with session.lock:
                    try:
                        path = session.store.frame_path(frame_id, annotated) if session.store else None
                        content = path.read_bytes() if path else None
                    except (KeyError, FileNotFoundError):
                        content = None
                    if content is None:
                        raise HTTPException(404, "Evidence frame unavailable")
                    return Response(content, media_type="image/jpeg" if annotated else "image/png", headers={"Cache-Control": "no-store", "X-Content-Type-Options": "nosniff"})
