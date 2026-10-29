"""Explicitly consented, bounded tabletop recording. This script never starts automatically."""
import bootstrap
import argparse
import datetime as dt
import json
from pathlib import Path
import time
import cv2
from steplock.sources.replay import inspect_video


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--consent",action="store_true",required=True,help="Operator has permission; no faces or sensitive material in view")
    parser.add_argument("--camera",type=int,default=0,choices=range(9))
    parser.add_argument("--seconds",type=int,default=20,choices=range(5,121))
    parser.add_argument("--output",required=True)
    args=parser.parse_args()
    output=Path(args.output).resolve()
    allowed=(bootstrap.ROOT/"fixtures/recorded").resolve()
    if not output.is_relative_to(allowed) or output.suffix.lower()!=".avi": parser.error("Output must be an AVI under fixtures/recorded/")
    if output.exists(): parser.error("Output exists; choose a new clip name")
    output.parent.mkdir(parents=True,exist_ok=True)
    cap=cv2.VideoCapture(args.camera,cv2.CAP_DSHOW if __import__('sys').platform=='win32' else cv2.CAP_ANY)
    writer=None
    try:
        if not cap.isOpened(): raise ValueError("Camera unavailable. Use browser capture or a consented phone recording instead.")
        cap.set(cv2.CAP_PROP_FRAME_WIDTH,960);cap.set(cv2.CAP_PROP_FRAME_HEIGHT,540)
        print("Recording consented tabletop. No audio. Keep anchors in frame; press Ctrl+C to stop.",flush=True)
        started=time.monotonic();count=0
        while time.monotonic()-started<args.seconds:
            ok,frame=cap.read()
            if not ok: raise ValueError("Camera stopped delivering frames")
            h,w=frame.shape[:2]
            if max(h,w)>1280: frame=cv2.resize(frame,(round(w*1280/max(h,w)),round(h*1280/max(h,w))))
            if writer is None:
                h,w=frame.shape[:2];writer=cv2.VideoWriter(str(output),cv2.VideoWriter_fourcc(*"MJPG"),5,(w,h))
                if not writer.isOpened(): raise ValueError("Video encoder unavailable")
            writer.write(frame);count+=1
            time.sleep(max(0,(count/5)-(time.monotonic()-started)))
    except KeyboardInterrupt: print("Recording stopped by operator.")
    finally:
        cap.release()
        if writer: writer.release()
    metadata={**inspect_video(output),"source_kind":"REPLAY_TAGGED","provenance":"OPERATOR_CONSENTED_STAGED_CAPTURE",
              "consent_recorded":True,"recorded_at":dt.datetime.now(dt.timezone.utc).isoformat(),"audio":False,
              "notice":"Manually review and label this clip before benchmark evaluation. Do not publish media without redistribution consent."}
    output.with_suffix(".capture.json").write_text(json.dumps(metadata,indent=2),encoding="utf-8")
    print(json.dumps(metadata,indent=2))


if __name__=="__main__": main()
