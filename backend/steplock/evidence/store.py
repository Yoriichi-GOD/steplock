from copy import deepcopy
import hashlib
import json
from pathlib import Path
import cv2


class EvidenceStore:
    def __init__(self, directory: Path, metadata):
        self.directory = directory
        self.frames = directory/"frames"
        self.frames.mkdir(parents=True,exist_ok=False)
        self.event_count=0
        self.frame_records={}
        self.metadata=deepcopy(metadata)
        with (directory/"source.json").open("x",encoding="utf-8") as file:
            json.dump(metadata,file,indent=2)

    def record_frame(self, record, original_png, overlay):
        if hashlib.sha256(original_png).hexdigest()!=record.frame_sha256:
            raise ValueError("Evidence bytes do not match perception hash")
        if record.frame_id in self.frame_records:
            raise ValueError("Frame IDs are immutable")
        original=self.frames/f"{record.frame_id}.png"
        annotated=self.frames/f"{record.frame_id}.jpg"
        original.write_bytes(original_png)
        ok,jpg=cv2.imencode(".jpg",overlay,[cv2.IMWRITE_JPEG_QUALITY,88])
        if not ok: raise ValueError("Overlay encoding failed")
        annotated.write_bytes(jpg.tobytes())
        value=record.model_dump(mode="json")
        value["overlay_sha256"]=hashlib.sha256(jpg.tobytes()).hexdigest()
        self.frame_records[record.frame_id]=value
        with (self.directory/"frames.jsonl").open("a",encoding="utf-8") as file:
            file.write(json.dumps(value,sort_keys=True)+"\n")

    def append_events(self, events):
        # Only append the unseen suffix. Check the prefix to catch accidental rewrites.
        path=self.directory/"events.jsonl"
        if self.event_count:
            prior=[json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
            if prior!=events[:self.event_count]:
                raise ValueError("Attempted event-history mutation")
        if len(events)<self.event_count: raise ValueError("Attempted event-history truncation")
        if len(events)>self.event_count:
            with path.open("a",encoding="utf-8") as file:
                for event in events[self.event_count:]:
                    file.write(json.dumps(event,sort_keys=True)+"\n")
            self.event_count=len(events)

    def frame_path(self, frame_id, annotated=True):
        if frame_id not in self.frame_records: raise KeyError(frame_id)
        return self.frames/f"{frame_id}{'.jpg' if annotated else '.png'}"
