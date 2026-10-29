"""Headless deterministic replay through the production service, with real saved evidence."""
import bootstrap
import argparse
import json
from pathlib import Path
from steplock.config import ROOT
from steplock.procedure.recipe import Recipe
from steplock.service import Session
from steplock.sources.replay import inspect_video, video_frames


def run(path,source_kind=None):
    path=Path(path).resolve()
    kind=source_kind or ("SYNTHETIC_FIXTURE" if path.is_relative_to(ROOT/"fixtures/synthetic") else "REPLAY_TAGGED")
    metadata=inspect_video(path)
    recipe=Recipe.load(ROOT/"recipes/tagged_four_part_v1.yaml")
    session=Session(recipe,kind,False,metadata)
    for index,ts,frame in video_frames(path):
        session.stats["frames_in"]+=1
        session.process(index,ts,frame)
    session.engine.checkpoint()
    session.store.append_events(session.engine.events)
    session.state="finished"
    report=session.snapshot()
    (session.directory/"report.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    print(json.dumps({"decision":report["decision"],"source_kind":kind,"source_sha256":report["source_sha256"],
        "frames_analyzed":report["runtime"]["frames_analyzed"],"events":len(report["events"]),"evidence_directory":str(session.directory)},indent=2))
    return report


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--replay",required=True)
    parser.add_argument("--source-kind",choices=["SYNTHETIC_FIXTURE","REPLAY_TAGGED"])
    args=parser.parse_args()
    run(args.replay,args.source_kind)
