from pathlib import Path
import hashlib
import cv2
from steplock.config import MAX_SECONDS


def hash_file(path):
    digest=hashlib.sha256()
    with Path(path).open("rb") as file:
        for chunk in iter(lambda:file.read(1024*1024),b""):
            digest.update(chunk)
    return digest.hexdigest()


def inspect_video(path):
    cap=cv2.VideoCapture(str(path))
    try:
        if not cap.isOpened(): raise ValueError("Video content could not be decoded")
        fps=float(cap.get(cv2.CAP_PROP_FPS))
        count=int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        ok,frame=cap.read()
        if not ok or frame is None: raise ValueError("Video contains no decodable frames")
        if not (1<=fps<=240) or count<1: raise ValueError("Video has invalid timing metadata")
        if count/fps>MAX_SECONDS+.05: raise ValueError(f"Video exceeds {MAX_SECONDS} second limit")
        h,w=frame.shape[:2]
        if min(h,w)<80 or max(h,w)>1920: raise ValueError("Use a video between 80px and 1920px per side")
        return {"fps":fps,"frame_count":count,"duration_ms":count/fps*1000,"width":w,"height":h,
                "timestamp_method":"FPS_INDEX_FALLBACK_DECLARED", "source_sha256":hash_file(path)}
    finally:
        cap.release()


def video_frames(path):
    metadata=inspect_video(path)
    cap=cv2.VideoCapture(str(path))
    try:
        index=0
        while index/metadata["fps"] <= MAX_SECONDS:
            ok,image=cap.read()
            if not ok: break
            # Explicit deterministic fallback avoids codec-specific nonmonotonic PTS.
            yield index,index/metadata["fps"]*1000,image
            index+=1
    finally:
        cap.release()
