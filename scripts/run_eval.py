"""Frozen-configuration three-arm evaluation over exactly the same decoded pixels."""
import bootstrap
import argparse
import csv
import datetime as dt
import hashlib
import json
import platform
import subprocess
import time
from pathlib import Path
import cv2
import numpy as np
import psutil
from steplock.procedure.recipe import Recipe
from steplock.procedure.engine import ProcedureEngine
from steplock.sources.replay import video_frames,hash_file
from steplock.vision.aruco import Detector
from scripts.eval_metrics import CLASSES,rates,wilson,match_events


def dump(path,value):
    path.write_text(json.dumps(value,indent=2,allow_nan=False),encoding="utf-8")


def csv_rows(path,rows,columns=None):
    with path.open("w",newline="",encoding="utf-8") as file:
        writer=csv.DictWriter(file,fieldnames=columns or list(rows[0]) if rows else columns or ["status"])
        writer.writeheader()
        writer.writerows(rows)


def git(*args):
    return subprocess.check_output(["git","-C",str(bootstrap.ROOT),*args],text=True).strip()


def run(split="test"):
    root=bootstrap.ROOT
    protocol=json.loads((root/"benchmarks/protocol.json").read_text(encoding="utf-8"))
    manifest=json.loads((root/"fixtures/synthetic/manifest.json").read_text(encoding="utf-8"))
    clips=[clip for clip in manifest["clips"] if clip["split"]==split]
    if not clips: raise ValueError("No clips in selected split")
    recipe=Recipe.load(root/"recipes/tagged_four_part_v1.yaml")
    now=dt.datetime.now(dt.timezone.utc)
    directory=root/"benchmarks/runs"/(now.strftime("%Y%m%d_%H%M%S_%f")+"_"+split)
    directory.mkdir(parents=True,exist_ok=False)
    (directory/"screenshots").mkdir()
    commit=git("rev-parse","HEAD")
    config={**protocol,"split":split,"git_commit":commit,"git_dirty":bool(git("status","--porcelain")),
            "git_status_at_start":git("status","--porcelain").splitlines(),
            "prediction_source_clean":not bool(git("diff","HEAD","--","backend/steplock","recipes")),
            "recipe_sha256":recipe.sha256,"protocol_sha256":hash_file(root/"benchmarks/protocol.json"),
            "manifest_sha256":hash_file(root/"fixtures/synthetic/manifest.json"),"created_at":now.isoformat()}
    dump(directory/"config.json",config)
    dump(directory/"environment.json",{"python":platform.python_version(),"platform":platform.platform(),"cpu":platform.processor(),
         "logical_cpus":psutil.cpu_count(),"cv_version":cv2.__version__,"numpy_version":np.__version__,"mode":"CPU","gpu_used":False,
         "capture_to_visible_alert_ms":None,"capture_to_visible_alert_status":"NOT_MEASURED"})
    csv_rows(directory/"source_manifest.csv",clips)
    all_rows=[];all_events=[];all_matches={name:[] for name in protocol["arms"]}
    per_class={name:{kind:[0,0,0] for kind in CLASSES} for name in protocol["arms"]}
    latencies=[];vision_times=[];calibration_valid=0;processed_frames=0
    opportunities=0;tag_tp=0;tag_fp=0;all_placed_opportunities=0;all_placed_tp=0;zone_opportunities=0;zone_correct=0
    unknown_opportunities=0;normal_minutes=0.;normal_fp={name:0 for name in protocol["arms"]}
    peak=psutil.Process().memory_info().rss
    started=time.perf_counter();active_processing_seconds=0.
    frame_log=(directory/"observations.jsonl").open("w",encoding="utf-8")
    try:
        for clip in clips:
            truth=json.loads((root/clip["truth_path"]).read_text(encoding="utf-8"))
            family=truth["family"]
            for gt in truth["frames"]:
                visible=[m for m in gt["markers"] if m["visible"]]
                opportunities+=len(visible)+(4 if gt["anchors_visible"] else 0)
                all_placed_opportunities+=len(gt["markers"])
                zone_opportunities+=len(visible)
            if family=="normal": normal_minutes+=clip["frame_count"]/clip["fps"]/60
            engines={name:ProcedureEngine(recipe,name) for name in protocol["arms"]}
            error=None;last_record=None;last_image=None;last_overlay=None
            clip_started=time.perf_counter()
            try:
                if clip["recipe_sha256"]!=recipe.sha256: raise ValueError("Frozen recipe hash differs from manifest")
                if hash_file(root/clip["relative_path"])!=clip["source_sha256"]: raise ValueError("Media hash mismatch")
                if hash_file(root/clip["truth_path"])!=clip["truth_sha256"]: raise ValueError("Truth hash mismatch")
                detector=Detector(recipe)
                for index,ts,image in video_frames(root/clip["relative_path"]):
                    if index>=len(truth["frames"]): raise ValueError("Decoded frame count exceeds annotation count")
                    record,_,overlay=detector.analyze(image,index,ts,clip["source_kind"],clip["source_sha256"])
                    last_record,last_image,last_overlay=record,image,overlay
                    gt=truth["frames"][index]
                    visible={m["marker_id"]:m["zone_id"] for m in gt["markers"] if m["visible"]}
                    expected=set(visible)|({40,41,42,43} if gt["anchors_visible"] else set())
                    observed=set(record.marker_ids)
                    tag_tp+=len(expected&observed);tag_fp+=len(observed-expected)
                    all_placed_tp+=len({m["marker_id"] for m in gt["markers"]}&observed)
                    zone_correct+=sum(ob.zone_id==visible[ob.marker_id] for ob in record.observations if ob.marker_id in visible)
                    calibration_valid+=record.calibration_id is not None
                    processed_frames+=1;vision_times.append(record.vision_ms)
                    latencies.append({"clip_id":clip["clip_id"],"frame_index":index,"source_time_ms":ts,"vision_ms":record.vision_ms})
                    frame_log.write(json.dumps({"clip_id":clip["clip_id"],**record.model_dump(mode="json")})+"\n")
                    for engine in engines.values(): engine.consume(record)
                    if index==0 and family in ("normal","wrong_order"):
                        cv2.imwrite(str(directory/"screenshots"/f"{clip['clip_id']}-start.jpg"),overlay)
                if last_record is None: raise ValueError("No decoded frames")
                if last_record.frame_index+1!=len(truth["frames"]): raise ValueError("Decoded video ended before annotated frames")
            except Exception as exc: error=f"{type(exc).__name__}: {exc}"
            active_processing_seconds+=time.perf_counter()-clip_started
            peak=max(peak,psutil.Process().memory_info().rss)
            for name,engine in engines.items():
                snapshot=engine.checkpoint() if not error else engine.snapshot()
                predicted=snapshot["decision"]["status"] if not error else "ERROR"
                matched=match_events(truth["events"],engine.events)
                all_matches[name].extend(matched["matches"])
                if family=="normal": normal_fp[name]+=matched["fp"]
                for kind in CLASSES:
                    counts=per_class[name][kind]
                    counts[0]+=sum(m["truth"]["kind"]==kind for m in matched["matches"])
                    counts[1]+=sum(e["kind"]==kind for e in matched["unmatched"])
                    counts[2]+=sum(e["kind"]==kind for e in matched["missed"])
                delays=[m["delay_ms"] for m in matched["matches"] if m["truth"]["kind"]!="MISSING_AT_CHECKPOINT"]
                row={"arm":name,"clip_id":clip["clip_id"],"family":family,"expected":truth["expected_final_status"],
                     "predicted":predicted,"correct":predicted==truth["expected_final_status"],
                     "tp":matched["tp"],"fp":matched["fp"],"fn":matched["fn"],"first_alert_delay_ms":min(delays) if delays else None,
                     "correction_expected":truth["correction_expected"],
                     "correction_detected":any(e["kind"]=="CORRECTED" for e in engine.events),
                     "uncertain_events":sum(e["kind"] in {"HOLD_UNCERTAIN","QUALITY_HOLD"} for e in engine.events),
                     "timely_count":sum(m["timely"] is True for m in matched["matches"]),
                     "timely_denominator":sum(e["boundary_ms"] is not None for e in truth["events"]),"error":error}
                all_rows.append(row)
                all_events.extend({"clip_id":clip["clip_id"],"arm":name,**e} for e in engine.events)
                if (not row["correct"] or row["fp"] or row["fn"]) and name=="steplock" and last_image is not None:
                    cv2.imwrite(str(directory/"screenshots"/f"{clip['clip_id']}-failure-original.jpg"),last_image)
                    cv2.imwrite(str(directory/"screenshots"/f"{clip['clip_id']}-failure-overlay.jpg"),last_overlay)
            print(f"{clip['clip_id']} {family}: "+" / ".join(f"{r['arm']}={r['predicted']}" for r in all_rows[-3:]),flush=True)
    finally: frame_log.close()
    arm_results=[]
    for name in protocol["arms"]:
        rows=[r for r in all_rows if r["arm"]==name]
        tp=sum(r["tp"] for r in rows);fp=sum(r["fp"] for r in rows);fn=sum(r["fn"] for r in rows)
        scores=rates(tp,fp,fn)
        correct=sum(r["correct"] for r in rows)
        nonpass=[r for r in rows if r["expected"]!="PASS"]
        confusion={e:{p:sum(r["expected"]==e and r["predicted"]==p for r in rows) for p in ("PASS","HOLD_FOR_REVIEW","ERROR","CALIBRATION_REQUIRED","PENDING")} for e in ("PASS","HOLD_FOR_REVIEW")}
        classes={kind:rates(*counts) for kind,counts in per_class[name].items()}
        class_f1=[v["f1"] for v in classes.values() if v["f1"] is not None]
        timely=sum(r["timely_count"] for r in rows);timed=sum(r["timely_denominator"] for r in rows)
        arm_results.append({"name":name,"clip_count":len(rows),"correct_final_status":correct,
            "final_status_accuracy":correct/len(rows),"final_status_accuracy_wilson95":wilson(correct,len(rows)),
            "event_precision":scores["precision"],"event_recall":scores["recall"],"event_f1":scores["f1"],
            "event_macro_f1":float(np.mean(class_f1)) if class_f1 else None,"tp":tp,"fp":fp,"fn":fn,
            "false_pass_count":sum(r["predicted"]=="PASS" for r in nonpass),"false_pass_denominator":len(nonpass),
            "unnecessary_hold_count":sum(r["expected"]=="PASS" and r["predicted"]!="PASS" for r in rows),
            "timely_count":timely,"timely_denominator":timed,"timely_recall":timely/timed if timed else None,
            "false_alerts_per_minute":normal_fp[name]/normal_minutes if normal_minutes else None,
            "corrections_detected":sum(r["correction_detected"] and r["correction_expected"] for r in rows),
            "corrections_expected":sum(r["correction_expected"] for r in rows),"uncertain_event_count":sum(r["uncertain_events"] for r in rows),
            "per_class":classes,"confusion_matrix":confusion})
    metrics={"created_at":now.isoformat(),"git_commit":commit,"git_dirty":config["git_dirty"],"source_kind":"SYNTHETIC_FIXTURE","split":split,
        "real_staged_data":"NOT_PROVIDED","clips":len(clips),"frames":processed_frames,
        "annotated_frames":sum(c["frame_count"] for c in clips),"arms":arm_results,"per_clip":all_rows,
        "vision":{"precision":tag_tp/(tag_tp+tag_fp) if tag_tp+tag_fp else None,"recall":tag_tp/opportunities if opportunities else None,
            "opportunities":opportunities,"tp":tag_tp,"fp":tag_fp,"missed":opportunities-tag_tp,
            "zone_accuracy":zone_correct/zone_opportunities if zone_opportunities else None,
            "zone_opportunities":zone_opportunities,"zone_correct":zone_correct,
            "all_placed_marker_recall":all_placed_tp/all_placed_opportunities if all_placed_opportunities else None,
            "calibration_valid_frames":calibration_valid,"calibration_denominator":sum(c["frame_count"] for c in clips),
            "unknown_rejection_rate":None,"unknown_opportunities":unknown_opportunities},
        "processing":{"vision_p50_ms":float(np.percentile(vision_times,50)) if vision_times else None,
            "vision_p95_ms":float(np.percentile(vision_times,95)) if vision_times else None,
            "throughput_fps":processed_frames/active_processing_seconds if active_processing_seconds else None,
            "peak_rss_mb":peak/1024**2,"capture_to_visible_alert_ms":None,
            "total_wall_seconds":time.perf_counter()-started,"frames_decoded":processed_frames,"frames_analyzed":processed_frames,"frames_dropped":0},
        "limitations":["Generated marker boards only. No physical camera or staged-real footage was evaluated.",
            "Held-out camera transform groups share a deterministic generator and recipe; this does not establish industrial generalization.",
            "Tag identity can be swapped. White-board emptiness cannot exclude uniform occluders or hidden stacked parts.",
            "Event F1 scores the four declared mistake classes; uncertainty/quality warnings are counted separately. All raw events are retained.",
            "False PASS denominator includes all annotated non-PASS clips, including quality/insufficient-evidence cases.",
            "Throughput is offline shared vision plus all three engines and logging. Capture-to-visible-alert, live CPU overhead and GPU performance were not measured.",
            "Wilson bounds are descriptive only: generated clips are related and not independent industrial samples."]}
    dump(directory/"metrics.json",metrics)
    csv_rows(directory/"results_per_clip.csv",all_rows)
    csv_rows(directory/"latency.csv",latencies)
    csv_rows(directory/"confusion_matrix.csv",[{"arm":a["name"],"expected":e,"predicted":p,"count":count} for a in arm_results for e,ps in a["confusion_matrix"].items() for p,count in ps.items()])
    with (directory/"events.jsonl").open("w",encoding="utf-8") as file:
        for event in all_events: file.write(json.dumps(event)+"\n")
    failures=[r for r in all_rows if not r["correct"] or r["fp"] or r["fn"]]
    (directory/"failures.md").write_text("# Retained failures and baseline limitations\n\n"+("\n".join(f"- {r['arm']} / {r['clip_id']} ({r['family']}): {r['expected']} → {r['predicted']}; TP/FP/FN {r['tp']}/{r['fp']}/{r['fn']}; {r['error'] or 'see raw events'}" for r in failures) or "No scored mismatches in this population. This does not establish physical validity.")+"\n",encoding="utf-8")
    summary=f"# Measured {split} run\n\n{len(clips)} synthetic clips, {processed_frames} decoded frames. Real staged data NOT_PROVIDED.\n\n| Arm | Final correct | Event P/R/F1 | False PASS | Timely |\n|---|---|---|---|---|\n"
    summary+="\n".join(f"| {a['name']} | {a['correct_final_status']}/{a['clip_count']} | {a['event_precision']} / {a['event_recall']} / {a['event_f1']} | {a['false_pass_count']}/{a['false_pass_denominator']} | {a['timely_count']}/{a['timely_denominator']} |" for a in arm_results)
    summary+=f"\n\nVision p50/p95 {metrics['processing']['vision_p50_ms']}/{metrics['processing']['vision_p95_ms']} ms. Offline throughput {metrics['processing']['throughput_fps']} fps. Capture-to-visible latency NOT_MEASURED.\n\nCommit {commit}; working tree dirty={config['git_dirty']}; prediction source clean={config['prediction_source_clean']}.\n\n"+"\n".join('- '+line for line in metrics["limitations"])+"\n"
    (directory/"summary.md").write_text(summary,encoding="utf-8")
    print(f"Saved immutable run: {directory}")
    return directory,metrics


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--split",choices=["dev","test"],default="test")
    args=parser.parse_args()
    run(args.split)
