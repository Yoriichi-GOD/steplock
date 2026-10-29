"""Measured synthetic degradation gates; separate from the predeclared clip-level score."""
import bootstrap
import datetime as dt
import hashlib
import json
import time
import cv2
import numpy as np
from scripts.fixture_lib import scenario_frames,render_board,paste_marker,ANCHOR_PIXELS,SLOTS,board_point
from steplock.procedure.recipe import Recipe
from steplock.procedure.engine import ProcedureEngine
from steplock.vision.aruco import Detector,png_bytes

HOLD={"HOLD_FOR_REVIEW","SOURCE_LOST","CALIBRATION_REQUIRED"}


def frames_for(case,seed):
    frames=list(scenario_frames("normal",variant=4,seed=seed))
    if case=="midassembly":
        final=frames[-1][3]
        frames=[(i,i*200,render_board(final,seed=seed+i+1,variant=4),final,None) for i in range(12)]
    if case=="repeated_pixels":
        image=render_board(frames[-1][3],variant=4)
        frames=[(i,i*200,image.copy(),frames[-1][3],None) for i in range(12)]
    if case=="unknown_tag":
        frames=[(i,ts,render_board([(10,"BASE_SLOT"),(30,"FASTENER_SLOT")],seed=seed+i+1),[(10,"BASE_SLOT"),(30,"FASTENER_SLOT")],None) for i,ts,_,_,_ in frames]
    for index,ts,image,placements,occluded in frames:
        image=image.copy()
        if case=="light_minus25": image=np.uint8(image.astype(float)*.75)
        if case=="light_minus50": image=np.uint8(image.astype(float)*.5)
        if case=="severe_blur": image=cv2.GaussianBlur(image,(41,41),0)
        if case=="occlusion" and index>=24:
            image=render_board(placements,seed=seed+index+1,variant=4,occluded="SPACER_SLOT")
        if case=="drop30" and index%10 in (1,4,7): continue
        if case=="backwards_time" and index==20: ts=0
        if case=="source_gap" and index>=20: ts+=5000
        if case=="anchors_lost" and index>=26: image=render_board(placements,seed=seed+index+1,anchors=False)
        if case=="extreme_tilt":
            src=np.float32([[0,0],[959,0],[959,599],[0,599]])
            dst=np.float32([[20,230],[940,230],[750,290],[180,290]])
            image=cv2.warpPerspective(image,cv2.getPerspectiveTransform(src,dst),(960,600),borderValue=(225,225,225))
        if case=="wrong_dictionary":
            image=render_board([],seed=0,anchors=False)
            dictionary=cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_50)
            positions={**ANCHOR_PIXELS,**{mid:board_point(*SLOTS[zone]) for mid,zone in placements}}
            for mid,center in positions.items():
                size=46 if mid>=40 else 56
                x,y=center[0]-size//2,center[1]-size//2
                cv2.rectangle(image,(x-8,y-8),(x+size+8,y+size+8),(255,255,255),-1)
                marker=cv2.aruco.generateImageMarker(dictionary,mid,size)
                image[y:y+size,x:x+size]=cv2.cvtColor(marker,cv2.COLOR_GRAY2BGR)
        yield index,ts,image


def main():
    cases=["clean","light_minus25","light_minus50","severe_blur","occlusion","repeated_pixels","drop30","extreme_tilt","wrong_dictionary","midassembly","backwards_time","anchors_lost","unknown_tag","source_gap"]
    strict={"severe_blur","occlusion","repeated_pixels","extreme_tilt","wrong_dictionary","midassembly","backwards_time","anchors_lost","unknown_tag","source_gap"}
    now=dt.datetime.now(dt.timezone.utc)
    directory=bootstrap.ROOT/"benchmarks/stress"/now.strftime("%Y%m%d_%H%M%S_%f")
    directory.mkdir(parents=True,exist_ok=False)
    recipe=Recipe.load(bootstrap.ROOT/"recipes/tagged_four_part_v1.yaml")
    rows=[];all_events=[];times=[];unknown_seen=0;unknown_total=0
    for case in cases:
        seed=902626
        frames=list(frames_for(case,seed))
        digest=hashlib.sha256()
        for _,_,image in frames: digest.update(png_bytes(image))
        source_hash=digest.hexdigest()
        detector,engine=Detector(recipe),ProcedureEngine(recipe)
        calibrated=0;flags={};last=None
        for index,ts,image in frames:
            record,png,overlay=detector.analyze(image,index,ts,"SYNTHETIC_FIXTURE",source_hash)
            engine.consume(record);calibrated+=record.calibration_id is not None
            for flag in record.quality_flags: flags[flag]=flags.get(flag,0)+1
            times.append(record.vision_ms);last=(image,overlay)
            if case=="unknown_tag":
                unknown_total+=1
                unknown_seen+=any(o.marker_id==30 and o.part_id=="UNKNOWN" for o in record.observations)
        result=engine.checkpoint()
        status=result["decision"]["status"]
        safe=status in HOLD if case in strict else status in HOLD|{"PASS"}
        if case=="midassembly" and any(e["kind"]=="ORDER_VIOLATION" for e in engine.events): safe=False
        if case=="repeated_pixels" and engine.confirmed: safe=False
        if case=="unknown_tag" and not any(e["kind"]=="UNKNOWN_COMPONENT" for e in engine.events): safe=False
        row={"case":case,"seed":seed,"source_kind":"SYNTHETIC_FIXTURE","source_hash_kind":"CONCATENATED_DECODED_PNG_STREAM",
             "source_sha256":source_hash,"frames_analyzed":len(frames),"calibration_valid_frames":calibrated,
             "expected":"HOLD / abstain" if case in strict else "Supported PASS or conservative HOLD", "status":status,
             "safe_gate_passed":safe,"reason_codes":result["decision"]["reason_codes"],"perception_flags":flags,
             "confirmed_steps":list(engine.confirmed)}
        rows.append(row);all_events.extend({"case":case,**e} for e in engine.events)
        cv2.imwrite(str(directory/f"{case}-original.jpg"),last[0]);cv2.imwrite(str(directory/f"{case}-overlay.jpg"),last[1])
        print(f"{case}: {status} safe_gate={safe}",flush=True)
    report={"created_at":now.isoformat(),"recipe_sha256":recipe.sha256,"source_kind":"SYNTHETIC_FIXTURE",
            "real_staged_data":"NOT_PROVIDED","cases":rows,"safe_gates_passed":sum(r["safe_gate_passed"] for r in rows),
            "case_count":len(rows),"vision_p50_ms":float(np.percentile(times,50)),"vision_p95_ms":float(np.percentile(times,95)),
            "unknown_tag_rejection":{"correct":unknown_seen,"opportunities":unknown_total,"rate":unknown_seen/unknown_total},
            "limits":["Designed synthetic safety checks, not an independent accuracy benchmark.",
                      "Light/drop cases permit abstention; a passing safety gate does not mean successful procedure completion.",
                      "No physical capture, hand recognition or uniform-occluder guarantee."]}
    (directory/"stress_metrics.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    with (directory/"events.jsonl").open("w",encoding="utf-8") as file:
        for event in all_events: file.write(json.dumps(event)+"\n")
    text="# Synthetic degradation gates\n\n| Stress | Status | Safety gate |\n|---|---|---|\n"+"\n".join(f"| {r['case']} | {r['status']} | {r['safe_gate_passed']} |" for r in rows)
    (directory/"summary.md").write_text(text+"\n\n"+"\n".join('- '+line for line in report["limits"])+"\n",encoding="utf-8")
    print(f"Saved {directory}")
    return report


if __name__=="__main__": main()
