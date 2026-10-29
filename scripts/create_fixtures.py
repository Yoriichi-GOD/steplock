"""Generate pixels and independent evaluation truth, never runtime predictions."""
import bootstrap
import argparse
import hashlib
import json
from pathlib import Path
import cv2
from scripts.fixture_lib import scenario_frames, WIDTH, HEIGHT
from steplock.procedure.recipe import Recipe
from steplock.sources.replay import hash_file

FAMILIES=("normal","wrong_component","wrong_zone","wrong_order","missing_fastener","correction","occlusion","frozen_capture")


def generate(variants=6,seed=2626):
    dest=bootstrap.ROOT/"fixtures/synthetic"
    dest.mkdir(parents=True,exist_ok=True)
    truth_dir=bootstrap.ROOT/"fixtures/truth"
    truth_dir.mkdir(parents=True,exist_ok=True)
    recipe=Recipe.load(bootstrap.ROOT/"recipes/tagged_four_part_v1.yaml")
    clips=[]
    catalog=[]
    for family_index,family in enumerate(FAMILIES):
        for variant in range(variants):
            clip_id=f"fx_{family_index:02d}_{variant:02d}"
            path=dest/f"{clip_id}.avi"
            truth_path=truth_dir/f"{clip_id}.json"
            writer=cv2.VideoWriter(str(path),cv2.VideoWriter_fourcc(*"MJPG"),5,(WIDTH,HEIGHT))
            if not writer.isOpened(): raise RuntimeError("MJPG video writer unavailable")
            frame_truth=[]
            try:
                for index,ts,frame,placements,occluded in scenario_frames(family,variant,seed+variant*1000):
                    writer.write(frame)
                    frame_truth.append({"frame_index":index,"source_time_ms":ts,
                        "markers":[{"marker_id":m,"zone_id":z,"visible":z!=occluded} for m,z in placements],
                        "anchors_visible":True,"occluded_zone":occluded})
            finally: writer.release()
            end=frame_truth[-1]["source_time_ms"]
            deviations=[]
            if family in ("wrong_component","correction"):
                deviations.append({"kind":"WRONG_COMPONENT","part_id":"WRONG_FASTENER","zone_id":"FASTENER_SLOT","onset_ms":4800,"boundary_ms":5600})
            if family=="wrong_zone":
                deviations.append({"kind":"WRONG_ZONE","part_id":"SPACER","zone_id":"COVER_SLOT","onset_ms":2400,"boundary_ms":3200})
            if family=="wrong_order":
                deviations.append({"kind":"ORDER_VIOLATION","part_id":"COVER","zone_id":"COVER_SLOT","onset_ms":2400,"boundary_ms":3200})
            missing={"wrong_component":["FASTENER"],"wrong_zone":["SPACER","COVER","FASTENER"],"wrong_order":["COVER","FASTENER"],"missing_fastener":["FASTENER"],"frozen_capture":["BASE","SPACER","COVER","FASTENER"]}.get(family,[])
            for part in missing:
                deviations.append({"kind":"MISSING_AT_CHECKPOINT","part_id":part,"zone_id":part+"_SLOT","onset_ms":end,"boundary_ms":None})
            expected="PASS" if family in ("normal","correction") else "HOLD_FOR_REVIEW"
            truth={"clip_id":clip_id,"source_kind":"SYNTHETIC_FIXTURE","family":family,
                   "expected_final_status":expected,"events":deviations,"frames":frame_truth,
                   "correction_expected":family=="correction","recipe_sha256":recipe.sha256,
                   "seed":seed+variant*1000,"variant":variant,"label_created_before_evaluation":True}
            truth_path.write_text(json.dumps(truth,indent=2),encoding="utf-8")
            clip={"clip_id":clip_id,"relative_path":path.relative_to(bootstrap.ROOT).as_posix(),
                  "truth_path":truth_path.relative_to(bootstrap.ROOT).as_posix(),"source_kind":"SYNTHETIC_FIXTURE",
                  "split":"dev" if variant<2 else "test","setup_group":f"camera_variant_{variant}",
                  "source_sha256":hash_file(path),"truth_sha256":hash_file(truth_path),"recipe_sha256":recipe.sha256,
                  "generator_sha256":hash_file(Path(__file__).with_name("fixture_lib.py")),
                  "seed":seed+variant*1000,"frame_count":len(frame_truth),"fps":5}
            clips.append(clip)
            if variant==0:
                catalog.append({"id":family,"title":family.replace("_"," ").title(),
                    "source_kind":"SYNTHETIC_FIXTURE","relative_path":clip["relative_path"],
                    "source_sha256":clip["source_sha256"],"duration_ms":len(frame_truth)*200})
    (dest/"manifest.json").write_text(json.dumps({"generator_version":1,"clips":clips},indent=2),encoding="utf-8")
    # Runtime catalog deliberately contains no expected verdicts or test labels.
    (dest/"catalog.json").write_text(json.dumps(catalog,indent=2),encoding="utf-8")
    print(f"Generated {len(clips)} synthetic clips ({sum(c['split']=='test' for c in clips)} held out), labels separate.")
    return clips


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--seed",type=int,default=2626)
    parser.add_argument("--variants",type=int,default=6,choices=range(1,7))
    args=parser.parse_args()
    generate(args.variants,args.seed)
