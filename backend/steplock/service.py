"""Bounded single-active-source orchestration, independent of HTTP and evaluation."""
from collections import deque
import datetime as dt
import hashlib
import json
import queue
import secrets
import threading
import time
from pathlib import Path
import numpy as np
from .config import ROOT, RUNTIME, MAX_SECONDS
from .evidence.store import EvidenceStore
from .procedure.engine import ProcedureEngine
from .sources.replay import video_frames
from .sources.camera import camera_frames
from .vision.aruco import Detector


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


class Session:
    def __init__(self, recipe, source_kind, consent, source_metadata=None, directory=None):
        self.id=secrets.token_hex(16)
        self.token=secrets.token_urlsafe(32)
        self.recipe=recipe
        self.source_kind=source_kind
        self.consent=consent
        self.source_metadata=source_metadata or {}
        self.source_hash=self.source_metadata.get("source_sha256") or hashlib.sha256(f"live-source-manifest:{self.id}".encode()).hexdigest()
        self.source_hash_kind="FILE_BYTES" if self.source_metadata.get("source_sha256") else "SESSION_SOURCE_MANIFEST"
        self.created_at=now()
        self.lock=threading.RLock()
        self.engine=ProcedureEngine(recipe)
        self.detector=Detector(recipe)
        self.state="ready"
        self.error=None
        self.latest=None
        self.last_frame_wall=None
        self.path=None
        self.camera_index=0
        self.capture_mode="backend"
        self.stop_event=threading.Event()
        self.frames=queue.Queue(maxsize=2)
        self.threads=[]
        self.vision_times=deque(maxlen=1800)
        self.stats={"frames_in":0,"frames_analyzed":0,"frames_dropped":0,"mode":"CPU","queue_capacity":2}
        self.human_reviews=[]
        self.manual_points=None
        self.store=None
        self.directory=directory or RUNTIME/"sessions"/self.id

    def initialize_store(self):
        if self.store is None:
            self.store=EvidenceStore(self.directory,{"session_id":self.id,"recipe":self.recipe.model_dump(mode="json"),
                "recipe_sha256":self.recipe.sha256,"source_kind":self.source_kind,"source_sha256":self.source_hash,
                "source_hash_kind":self.source_hash_kind,"source_metadata":self.source_metadata,
                "consent_recorded":self.consent,"created_at":self.created_at,"advisory_only":True})

    def process(self,index,timestamp,image):
        with self.lock:
            self.initialize_store()
            record,png,overlay=self.detector.analyze(image,index,timestamp,self.source_kind,self.source_hash,self.manual_points)
            self.store.record_frame(record,png,overlay)
            self.engine.consume(record)
            self.store.append_events(self.engine.events)
            self.stats["frames_analyzed"]+=1
            self.vision_times.append(record.vision_ms)
            self.latest=record
            self.last_frame_wall=time.monotonic()
            return record

    def _enqueue(self,item):
        try: self.frames.put_nowait(item)
        except queue.Full:
            try: self.frames.get_nowait()
            except queue.Empty: pass
            self.stats["frames_dropped"]+=1
            self.frames.put_nowait(item)

    def start(self, *, auto_checkpoint=False, on_done=lambda:None):
        with self.lock:
            if self.state!="ready": raise ValueError("This session has already started; create a new session")
            if self.source_kind=="LIVE_TAGGED" and not self.consent: raise ValueError("Camera consent is required")
            if self.source_kind!="LIVE_TAGGED" and self.path is None: raise ValueError("Upload a video before starting")
            self.initialize_store()
            self.state="running"
            self.last_frame_wall=time.monotonic()
            if self.capture_mode=="browser": return

        def produce():
            source=None
            try:
                source=camera_frames(self.camera_index,self.stop_event) if self.source_kind=="LIVE_TAGGED" else video_frames(self.path)
                began=time.monotonic()
                last_selected=-1000.
                for index,ts,image in source:
                    if self.stop_event.is_set(): break
                    self.stats["frames_in"]+=1
                    if self.source_kind!="LIVE_TAGGED":
                        if self.stop_event.wait(max(0.,ts/1000-(time.monotonic()-began))): break
                    # Analyze at most 10fps. Every intentional skip is counted.
                    if ts-last_selected<95:
                        self.stats["frames_dropped"]+=1
                        continue
                    last_selected=ts
                    self._enqueue((index,ts,image))
            except Exception as exc:
                with self.lock: self.error=str(exc)
            finally:
                if source is not None: source.close()
                # Preserve queued frames on EOF rather than discarding the last placement.
                while True:
                    try:
                        self.frames.put(None,timeout=.2)
                        break
                    except queue.Full:
                        if not consumer.is_alive(): break

        def consume():
            try:
                while True:
                    item=self.frames.get()
                    if item is None: break
                    if not self.stop_event.is_set(): self.process(*item)
                with self.lock:
                    if self.error or self.stop_event.is_set() or self.source_kind=="LIVE_TAGGED":
                        self.engine.source_lost(self.error or "Capture stopped. Start a new session to continue.")
                        self.state="error" if self.error else "stopped"
                    else:
                        self.state="finished"
                        if auto_checkpoint: self.engine.checkpoint()
                    self.store.append_events(self.engine.events)
            except Exception as exc:
                with self.lock:
                    self.error=str(exc)
                    self.engine.source_lost("Analysis failed; inspect the error and restart.")
                    self.state="error"
                    self.stop_event.set()
                    if self.store: self.store.append_events(self.engine.events)
            finally: on_done()

        consumer=threading.Thread(target=consume,name=f"steplock-infer-{self.id[:6]}",daemon=True)
        producer=threading.Thread(target=produce,name=f"steplock-source-{self.id[:6]}",daemon=True)
        self.threads=[producer,consumer]
        consumer.start()
        producer.start()

    def stop(self):
        self.stop_event.set()
        for thread in self.threads:
            thread.join(timeout=3)
        with self.lock:
            if any(t.is_alive() for t in self.threads):
                self.state="stopping"
            elif self.state!="stopped":
                self.engine.source_lost()
                self.state="stopped"
                if self.store: self.store.append_events(self.engine.events)

    def snapshot(self):
        with self.lock:
            if self.source_kind=="LIVE_TAGGED" and self.state=="running" and self.last_frame_wall is not None and (time.monotonic()-self.last_frame_wall)*1000>self.recipe.maximum_observation_gap_ms:
                self.engine.source_lost("No fresh camera frame within the recipe freshness window.")
                self.stop_event.set()
                self.state="source_lost"
                if self.store: self.store.append_events(self.engine.events)
            snapshot=self.engine.snapshot()
            times=list(self.vision_times)
            return {**snapshot,"session_id":self.id,"recipe_id":self.recipe.recipe_id,
                "recipe_sha256":self.recipe.sha256,"recipe_version":self.recipe.version,
                "source_kind":self.source_kind,"source_sha256":self.source_hash,"source_hash_kind":self.source_hash_kind,
                "source_metadata":self.source_metadata,"consent_recorded":self.consent,
                "state":self.state,"error":self.error,"created_at":self.created_at,"last_updated_at":now(),
                "latest_frame":self.latest.model_dump(mode="json") if self.latest else None,
                "runtime":{**self.stats,"cv_version":__import__('cv2').__version__,
                    "vision_p50_ms":float(np.percentile(times,50)) if times else None,
                    "vision_p95_ms":float(np.percentile(times,95)) if times else None,
                    "capture_to_visible_alert_ms":None},
                "human_reviews":list(self.human_reviews)}


class SessionManager:
    def __init__(self):
        self.sessions={}
        self.active_id=None
        self.lock=threading.RLock()

    def start(self,session,auto_checkpoint=False):
        with self.lock:
            active=self.sessions.get(self.active_id)
            if active and active.state in {"running","stopping"}: raise RuntimeError("Another source is active; stop it first")
            self.active_id=session.id
            try:
                session.start(auto_checkpoint=auto_checkpoint,on_done=lambda:self.release(session.id))
            except Exception:
                self.active_id=None
                raise

    def release(self,session_id):
        with self.lock:
            if self.active_id==session_id: self.active_id=None

    def stop_all(self):
        for session in list(self.sessions.values()):
            if session.state in {"running","stopping","source_lost"}: session.stop()
