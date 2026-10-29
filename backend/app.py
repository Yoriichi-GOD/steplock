"""STEPLOCK local API and same-origin production frontend. No cloud service required."""
from contextlib import asynccontextmanager
import json
import os
from pathlib import Path
import secrets
import sys
import time
sys.path.insert(0,str(Path(__file__).resolve().parent))
import cv2
import numpy as np
from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.trustedhost import TrustedHostMiddleware
from pydantic import BaseModel, ConfigDict, Field
from steplock.config import ROOT, RUNTIME, MAX_UPLOAD, MAX_SECONDS
from steplock.demo_recording import PINNED_ID, RECORDING_PATH, pinned_recording
from steplock.evidence.report import html_report
from steplock.procedure.recipe import Recipe
from steplock.schemas import SourceKind
from steplock.service import Session, SessionManager
from steplock.sources.replay import inspect_video
from steplock.vision.calibration import calibrate


class CreateSession(BaseModel):
    model_config=ConfigDict(extra="forbid")
    recipe_id: str="tagged_four_part_v1"
    source_kind: SourceKind="SYNTHETIC_FIXTURE"
    example_id: str | None=None
    consent_recorded: bool=False
    camera_mode: str=Field(default="browser",pattern="^(browser|backend)$")
    camera_index: int=Field(default=0,ge=0,le=8)


class StartSession(BaseModel):
    checkpoint_at_end: bool=False


class Review(BaseModel):
    event_id: str
    note: str=Field(default="Acknowledged by operator",max_length=500)


class Calibration(BaseModel):
    points: list[tuple[float,float]]=Field(min_length=4,max_length=4)


def catalog():
    path=ROOT/"fixtures/synthetic/catalog.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else []


def latest_run():
    candidates=sorted(p for p in (ROOT/"benchmarks/runs").glob("*") if p.is_dir() and (p/"metrics.json").exists())
    return candidates[-1] if candidates else None


def create_app(runtime_root=None):
    runtime=Path(runtime_root) if runtime_root is not None else RUNTIME
    manager=SessionManager()
    recipes={}
    for path in (ROOT/"recipes").glob("*.yaml"):
        recipe=Recipe.load(path)
        recipes[recipe.recipe_id]=recipe
    for path in (runtime/"recipes").glob("*.json"):
        recipe=Recipe.model_validate_json(path.read_text(encoding="utf-8"))
        recipes[f"{recipe.recipe_id}:v{recipe.version}"]=recipe

    @asynccontextmanager
    async def lifespan(app):
        yield
        manager.stop_all()

    app=FastAPI(title="STEPLOCK",version="1.0.0",lifespan=lifespan)
    app.state.manager=manager
    app.state.recipes=recipes
    app.add_middleware(TrustedHostMiddleware,allowed_hosts=["127.0.0.1","localhost"])
    allowed=[origin for origin in os.environ.get("STEPLOCK_ALLOWED_ORIGINS","").split(",") if origin]
    app.add_middleware(CORSMiddleware,allow_origins=allowed,allow_credentials=False,
                       allow_methods=["GET","POST","PUT","DELETE"],allow_headers=["Authorization","Content-Type"])

    @app.middleware("http")
    async def origin_guard(request: Request,call_next):
        origin=request.headers.get("origin")
        if origin and origin.rstrip("/")!=str(request.base_url).rstrip("/") and origin not in allowed:
            return JSONResponse({"detail":"This local application accepts only its configured browser origin."},status_code=403)
        if request.method=="POST" and request.url.path=="/api/recipes":
            raw=await request.body()
            if len(raw)>65536: return JSONResponse({"detail":"Recipe exceeds the 64 KiB limit"},status_code=413)
            def unique_keys(pairs):
                result={}
                for key,value in pairs:
                    if key in result: raise ValueError(f"Duplicate recipe key: {key}")
                    result[key]=value
                return result
            try: json.loads(raw,object_pairs_hook=unique_keys)
            except ValueError as exc: return JSONResponse({"detail":str(exc)},status_code=422)
        response=await call_next(request)
        response.headers["X-Content-Type-Options"]="nosniff"
        response.headers["Referrer-Policy"]="no-referrer"
        if request.url.path.startswith("/api/sessions"): response.headers["Cache-Control"]="no-store"
        return response

    def get_session(sid,request):
        session=manager.sessions.get(sid)
        if session is None: raise HTTPException(404,"Session not found")
        supplied=request.headers.get("authorization","").removeprefix("Bearer ")
        if not secrets.compare_digest(supplied,session.token): raise HTTPException(403,"Session access token is required")
        return session

    @app.get("/api/health")
    def health():
        active=manager.sessions.get(manager.active_id)
        return {"status":"ok","cv_version":cv2.__version__,"aruco_available":hasattr(cv2.aruco,"ArucoDetector"),
                "camera_active":bool(active and active.source_kind=="LIVE_TAGGED" and active.state=="running"),
                "active_session_id":manager.active_id,"advisory_only":True,"real_staged_data":"NOT_PROVIDED"}

    @app.get("/api/recipes")
    def list_recipes():
        return [{"key":key,**recipe.model_dump(mode="json"),"sha256":recipe.sha256} for key,recipe in recipes.items()]

    @app.post("/api/recipes",status_code=201)
    def save_recipe(recipe: Recipe):
        versions=[r.version for r in recipes.values() if r.recipe_id==recipe.recipe_id]
        if versions and recipe.version<=max(versions): raise HTTPException(409,"Increment the recipe version; existing sessions are immutable")
        key=f"{recipe.recipe_id}:v{recipe.version}"
        recipes[key]=recipe
        directory=runtime/"recipes"
        directory.mkdir(parents=True,exist_ok=True)
        path=directory/f"{recipe.sha256}.json"
        if not path.exists():
            with path.open("x",encoding="utf-8") as file: json.dump(recipe.model_dump(mode="json"),file,indent=2)
        return {"key":key,"sha256":recipe.sha256,"recipe":recipe.model_dump(mode="json")}

    @app.get("/api/demo/scenarios")
    def scenarios():
        return {"scenarios":[{k:v for k,v in row.items() if k!="relative_path"} for row in catalog()],
                "pinned_recording":pinned_recording(),
                "real_staged_data":"NOT_PROVIDED","notice":"Examples are generated software tests, not camera footage."}

    @app.post("/api/sessions",status_code=201)
    def create_session(data: CreateSession):
        if data.recipe_id not in recipes: raise HTTPException(404,"Unknown recipe")
        if data.source_kind in {"LIVE_TAGGED","REPLAY_TAGGED"} and not data.consent_recorded: raise HTTPException(400,"Confirm consent for camera footage before starting")
        if len(manager.sessions)>=64: raise HTTPException(429,"Session limit reached. Restart the local server to begin a new group.")
        metadata={}
        source=None
        if data.example_id:
            if data.example_id==PINNED_ID:
                if data.source_kind!="REPLAY_TAGGED": raise HTTPException(400,"The real recording must use the replay source type")
                source=pinned_recording()
                if source is None: raise HTTPException(404,"The pinned real recording is unavailable locally. Upload a recording or select a synthetic example.")
                path=RECORDING_PATH
                metadata={**source,**inspect_video(path),"provenance":"LOCAL_LICENSED_DATASET_EXCERPT"}
            else:
                if data.source_kind!="SYNTHETIC_FIXTURE": raise HTTPException(400,"Generated examples must be labeled SYNTHETIC_FIXTURE")
                source=next((row for row in catalog() if row["id"]==data.example_id),None)
                if source is None: raise HTTPException(404,"Unknown example. Generate fixtures first.")
                path=(ROOT/source["relative_path"]).resolve()
                if not path.is_relative_to(ROOT/"fixtures/synthetic") or not path.is_file(): raise HTTPException(404,"Example media is unavailable")
                metadata=inspect_video(path)
        session=Session(recipes[data.recipe_id],data.source_kind,data.consent_recorded,metadata)
        session.directory=runtime/"sessions"/session.id
        if source: session.path=path
        session.camera_index=data.camera_index
        session.capture_mode=data.camera_mode if data.source_kind=="LIVE_TAGGED" else "backend"
        manager.sessions[session.id]=session
        return {"session_id":session.id,"access_token":session.token,"snapshot":session.snapshot()}

    @app.get("/api/sessions/{sid}")
    def snapshot(sid: str,request: Request): return get_session(sid,request).snapshot()

    @app.post("/api/sessions/{sid}/upload")
    async def upload(sid: str,request: Request,file: UploadFile=File(...)):
        session=get_session(sid,request)
        if session.state!="ready" or session.store is not None or session.source_kind=="LIVE_TAGGED": raise HTTPException(409,"Upload only to a new replay session")
        if not file.filename or any(c in file.filename for c in ("/","\\","\x00")) or file.filename in {".",".."}:
            await file.close()
            raise HTTPException(400,"Use a plain video filename without path components")
        if file.content_type not in {"video/mp4","video/avi","video/x-msvideo","video/quicktime","video/webm"}:
            await file.close()
            raise HTTPException(415,"Upload an MP4, AVI, MOV or WebM video")
        session.directory.mkdir(parents=True,exist_ok=True)
        path=session.directory/"upload.bin"
        if path.exists(): raise HTTPException(409,"An upload is already present")
        total=0
        try:
            with path.open("xb") as target:
                while chunk:=await file.read(1024*1024):
                    total+=len(chunk)
                    if total>MAX_UPLOAD: raise HTTPException(413,"Video exceeds the configured upload size limit")
                    target.write(chunk)
            try: metadata=inspect_video(path)
            except ValueError as exc: raise HTTPException(422,str(exc)) from exc
            with session.lock:
                session.source_metadata={**metadata,"provenance":"USER_DECLARED_RECORDING","bytes":total}
                session.source_hash=metadata["source_sha256"]
                session.source_hash_kind="FILE_BYTES"
                session.path=path
            return {"uploaded":True,"source_sha256":session.source_hash,"metadata":session.source_metadata}
        except Exception:
            path.unlink(missing_ok=True)
            raise
        finally: await file.close()

    @app.post("/api/sessions/{sid}/start")
    def start(sid: str,data: StartSession,request: Request):
        session=get_session(sid,request)
        try: manager.start(session,data.checkpoint_at_end)
        except (ValueError,RuntimeError) as exc: raise HTTPException(409,str(exc)) from exc
        return session.snapshot()

    @app.post("/api/sessions/{sid}/stop")
    def stop(sid: str,request: Request):
        session=get_session(sid,request)
        session.stop()
        if session.state!="stopping": manager.release(sid)
        return session.snapshot()

    @app.post("/api/sessions/{sid}/checkpoint")
    def checkpoint(sid: str,request: Request):
        session=get_session(sid,request)
        with session.lock:
            if session.latest is None: raise HTTPException(409,"No frame has been analyzed")
            session.engine.checkpoint()
            session.store.append_events(session.engine.events)
            return session.snapshot()

    @app.post("/api/sessions/{sid}/review")
    def review(sid: str,data: Review,request: Request):
        session=get_session(sid,request)
        with session.lock:
            if not any(e["event_id"]==data.event_id for e in session.engine.events): raise HTTPException(404,"Event not found")
            record={**data.model_dump(),"reviewed_at":time.time(),"effect":"ACKNOWLEDGEMENT_ONLY_VERDICT_UNCHANGED"}
            session.human_reviews.append(record)
            if session.store:
                with (session.directory/"reviews.jsonl").open("a",encoding="utf-8") as file: file.write(json.dumps(record)+"\n")
            return record

    @app.post("/api/sessions/{sid}/calibration")
    def calibration(sid: str,data: Calibration,request: Request):
        session=get_session(sid,request)
        with session.lock:
            if session.latest is None: raise HTTPException(409,"Analyze a frame before selecting calibration points")
            try: calibrate(data.points,(session.latest.height,session.latest.width,3))
            except ValueError as exc: raise HTTPException(422,str(exc)) from exc
            session.manual_points=data.points
            session.manual_calibrated_at_ms=session.latest.captured_at_ms
            return {"calibration_mode":"MANUAL_FOUR_POINT","valid_for_ms":session.recipe.maximum_observation_gap_ms,"notice":"Brief fixed-camera fallback. Manual calibration expires without visible anchors; automatic anchors take precedence."}

    @app.post("/api/sessions/{sid}/frame")
    async def browser_frame(sid: str,request: Request,captured_at_ms: float):
        session=get_session(sid,request)
        if session.source_kind!="LIVE_TAGGED" or session.capture_mode!="browser" or session.state!="running": raise HTTPException(409,"No active browser camera session")
        if not 0<=captured_at_ms<=MAX_SECONDS*1000: raise HTTPException(422,"Camera timestamp outside the session duration limit")
        if request.headers.get("content-type")!="image/jpeg": raise HTTPException(415,"Camera frames must be JPEG")
        raw=bytearray()
        async for chunk in request.stream():
            raw.extend(chunk)
            if len(raw)>2*1024*1024: raise HTTPException(413,"Camera image too large")
        image=cv2.imdecode(np.frombuffer(raw,np.uint8),cv2.IMREAD_COLOR)
        if image is None or max(image.shape[:2])>1280: raise HTTPException(422,"Invalid camera image; maximum side is 1280px")
        session.stats["frames_in"]+=1
        session.process(session.stats["frames_in"]-1,captured_at_ms,image)
        return {"accepted":True,"frame_id":session.latest.frame_id,"decision":session.engine.snapshot()["decision"]}

    @app.get("/api/sessions/{sid}/events")
    def events(sid: str,request: Request): return {"events":get_session(sid,request).snapshot()["events"]}

    @app.get("/api/sessions/{sid}/frames")
    def frame_index(sid: str,request: Request):
        session=get_session(sid,request)
        with session.lock:
            return {"frames":[{"frame_id":f["frame_id"],"source_time_ms":f["captured_at_ms"],"frame_index":f["frame_index"]} for f in session.store.frame_records.values()] if session.store else []}

    @app.get("/api/sessions/{sid}/frames/{frame_id}")
    def frame_image(sid: str,frame_id: str,request: Request,annotated: bool=True):
        session=get_session(sid,request)
        try: path=session.store.frame_path(frame_id,annotated) if session.store else None
        except KeyError as exc: raise HTTPException(404,"Frame not found") from exc
        if path is None: raise HTTPException(404,"No evidence frame")
        return FileResponse(path,media_type="image/jpeg" if annotated else "image/png")

    @app.get("/api/sessions/{sid}/report")
    def report(sid: str,request: Request,format: str="json"):
        snapshot=get_session(sid,request).snapshot()
        if format=="html": return HTMLResponse(html_report(snapshot),headers={"Content-Disposition":f'attachment; filename="steplock-{sid[:8]}.html"'})
        if format!="json": raise HTTPException(422,"Report format must be json or html")
        return JSONResponse(snapshot,headers={"Content-Disposition":f'attachment; filename="steplock-{sid[:8]}.json"'})

    @app.delete("/api/sessions/{sid}/upload")
    def delete_upload(sid: str,request: Request):
        session=get_session(sid,request)
        if session.state in {"running","stopping"}: raise HTTPException(409,"Stop the source before removing the temporary upload")
        upload=session.directory/"upload.bin"
        existed=upload.exists()
        upload.unlink(missing_ok=True)
        session.path=None
        return {"temporary_upload_removed":existed,"evidence_retained":True}

    @app.get("/api/benchmarks/latest")
    def benchmark():
        directory=latest_run()
        if not directory: return {"status":"NOT_RUN","real_staged_data":"NOT_PROVIDED","reason":"Run scripts/run_eval.py first"}
        return {"status":"MEASURED","run_id":directory.name,**json.loads((directory/"metrics.json").read_text(encoding="utf-8"))}

    @app.get("/api/benchmarks/latest/artifacts/{filename}")
    def benchmark_artifact(filename: str):
        allowed={"metrics.json","summary.md","results_per_clip.csv","confusion_matrix.csv","failures.md","latency.csv","environment.json","config.json","source_manifest.csv"}
        directory=latest_run()
        if filename not in allowed or directory is None or not (directory/filename).is_file(): raise HTTPException(404,"Artifact not found")
        return FileResponse(directory/filename,filename=filename)

    app.mount("/api/demo-kit",StaticFiles(directory=ROOT/"demo_kit"),name="demo-kit")
    if (ROOT/"frontend/dist").is_dir(): app.mount("/",StaticFiles(directory=ROOT/"frontend/dist",html=True),name="studio")
    return app


app=create_app()
