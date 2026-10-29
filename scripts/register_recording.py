"""Register a manually labeled, consented real clip before evaluation; never guesses truth."""
import bootstrap
import argparse
import csv
import json
from pathlib import Path
import re
import shutil
from steplock.procedure.recipe import Recipe
from steplock.sources.replay import inspect_video


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file",required=True)
    parser.add_argument("--clip-id",required=True)
    parser.add_argument("--scenario",required=True,choices=["normal","wrong_component","wrong_zone","wrong_order","missing_fastener","correction","occlusion"])
    parser.add_argument("--expected",required=True,choices=["PASS","HOLD_FOR_REVIEW"])
    parser.add_argument("--reason",default="")
    parser.add_argument("--onset-ms",type=float)
    parser.add_argument("--boundary-ms",type=float)
    parser.add_argument("--operator-group",required=True,help="Anonymous group, not a person's name")
    parser.add_argument("--camera-position",required=True)
    parser.add_argument("--consent",required=True,action="store_true")
    args=parser.parse_args()
    if not re.fullmatch(r"[a-zA-Z0-9_-]{1,60}",args.clip_id): parser.error("Use an opaque clip ID with letters, digits, _ or -")
    if args.scenario in {"wrong_component","wrong_zone","wrong_order","correction"} and args.onset_ms is None: parser.error("Annotate error onset before evaluation")
    path=Path(args.file).resolve()
    metadata=inspect_video(path)
    if args.onset_ms is not None and not 0<=args.onset_ms<=metadata["duration_ms"]: parser.error("Onset lies outside recording")
    if args.boundary_ms is not None and not (args.onset_ms is not None and args.onset_ms<=args.boundary_ms<=metadata["duration_ms"]): parser.error("Boundary must follow onset within the clip")
    dest=bootstrap.ROOT/"fixtures/recorded"/f"{args.clip_id}{path.suffix.lower()}"
    if dest.exists() and dest!=path: parser.error("Registered clip path already exists; no overwrite")
    dest.parent.mkdir(parents=True,exist_ok=True)
    if path!=dest: shutil.copy2(path,dest)
    recipe=Recipe.load(bootstrap.ROOT/"recipes/tagged_four_part_v1.yaml")
    row={"clip_id":args.clip_id,"relative_path":dest.relative_to(bootstrap.ROOT).as_posix(),"source_kind":"REPLAY_TAGGED",
         "scenario":args.scenario,"expected_final_status":args.expected,"expected_reason":args.reason,"onset_ms":args.onset_ms,
         "boundary_ms":args.boundary_ms,"operator_group":args.operator_group,"camera_position":args.camera_position,
         "recipe_sha256":recipe.sha256,"source_sha256":metadata["source_sha256"],"consent_recorded":True}
    manifest=bootstrap.ROOT/"fixtures/recorded/manifest.csv"
    existing=list(csv.DictReader(manifest.open(newline="",encoding="utf-8"))) if manifest.exists() else []
    if any(old["clip_id"]==args.clip_id for old in existing): parser.error("Clip ID already registered; preserve original labels")
    with manifest.open("a",newline="",encoding="utf-8") as file:
        writer=csv.DictWriter(file,fieldnames=list(row))
        if not existing and not manifest.stat().st_size: writer.writeheader()
        writer.writerow(row)
    print(json.dumps({"registered":row,"scope":"Manual clip-level annotation; review complete event labels separately before event-level scoring.",
                      "public_media":"NOT_AUTHORIZED; recorded media remain ignored by Git"},indent=2))


if __name__=="__main__": main()
