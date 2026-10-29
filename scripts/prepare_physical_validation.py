"""Create a 20-trial physical recording kit without opening any camera."""
try:
    from . import bootstrap
except ImportError:
    import bootstrap
import argparse
import csv
import datetime as dt
import json
from pathlib import Path
import shutil
from steplock.procedure.recipe import Recipe


SCENARIOS = {
    "normal": "Start empty; place BASE, SPACER, COVER, FASTENER in recipe order; pause after each.",
    "wrong_component": "Start empty; place BASE, SPACER, COVER, then tag 14 wrong fastener; retain the fault.",
    "wrong_order": "Start empty; place COVER before SPACER; then finish without re-placing COVER.",
    "missing_fastener": "Start empty; place BASE, SPACER, COVER only; request final checkpoint.",
    "correction": "Start empty; build through COVER; place tag 14; pause; remove it; place tag 13; finish."
}


def prepare(output):
    output = Path(output).resolve()
    if not output.is_relative_to(bootstrap.ROOT.resolve()):
        raise ValueError("Keep the kit inside this checkout")
    output.mkdir(parents=True, exist_ok=False)
    recipe = Recipe.load(bootstrap.ROOT / "recipes/tagged_four_part_v1.yaml")
    rows = []
    for scenario, instruction in SCENARIOS.items():
        for variant in range(4):
            rows.append({"clip_id": f"real_{scenario}_{variant+1:02d}", "scenario": scenario,
                         "setup": "overhead_A" if variant < 2 else "angled_B",
                         "expected_final_status": "PASS" if scenario in ("normal", "correction") else "HOLD_FOR_REVIEW",
                         "recipe_sha256": recipe.sha256, "instructions": instruction,
                         "recording_status": "NOT_RECORDED", "source_sha256": "", "operator_group": "", "consent_recorded": ""})
    with (output / "trial_plan.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    labels = {"population": "REAL_STAGED", "annotation_status": "PENDING", "reviewed_before_inference": False,
              "capture_provenance": "REQUIRED: describe actual camera/device and physical objects; no generated or screen-replayed fixtures",
              "recipe_sha256": recipe.sha256, "clips": [],
              "clip_schema_example_NOT_A_RECORDING": {
                  "clip_id": "opaque_registered_id", "source_sha256": "REPLACE_WITH_ACTUAL_FILE_HASH",
                  "event_annotation_complete": True, "correction_expected": False,
                  "events": [{"kind": "WRONG_COMPONENT", "part_id": "WRONG_FASTENER", "zone_id": "FASTENER_SLOT",
                              "onset_ms": 4000, "boundary_ms": 6000}],
                  "frames": [{"frame_index": 0, "visible_markers": {"40": None, "41": None, "42": None, "43": None},
                              "notes": "Manually annotated visible tag IDs. Component values are recipe zone IDs or null."}]}}
    (output / "manual_labels_TEMPLATE.json").write_text(json.dumps(labels, indent=2), encoding="utf-8")
    for filename in ("printable_board.png", "markers.png"):
        shutil.copy2(bootstrap.ROOT / "demo_kit" / filename, output / filename)
    text = """# STEPLOCK physical recording kit

No physical footage has been recorded or scored by this kit. Template example
labels are documentation only and are never treated as observations or truth.

1. Print the board and marker sheet. Attach tags 10–14 to separate harmless physical
   objects. The four fixed anchors 40–43 must remain visible. Use real objects moved
   on the physical board, not a screen replay, generated scene, or added digital tags.
2. Follow trial_plan.csv: five scenarios × four independent recordings, with two
   camera setups. Start with a clear empty board for at least one second. Pause at
   least 0.6 s after placements, removals and corrections. Keep the final state moving
   slightly/independently visible for a second. Do not hide or delete failed trials.
3. Record without faces or audio and obtain participant consent. Phone recordings
   work; use 80–1920 px per side, 1–240 fps, at most 120 seconds and 50 MiB per app
   upload. A camera is never opened by the kit generator.
4. Optional webcam recording from this repo (explicit operator consent required):
   python scripts/record_clip.py --consent --camera 0 --seconds 20 --output fixtures/recorded/real_01.avi
5. Review the actual clip before running inference. Register it with the existing
   scripts/register_recording.py; supply opaque clip ID, scenario, expected verdict,
   onset/boundary timing, anonymous operator group, camera position, and --consent.
   The registration tool copies the original media and hashes it; it does not guess truth.
6. Copy manual_labels_TEMPLATE.json to ignored data/physical_labels.json, remove
   the schema example, and manually add the registered clips. Mark population
   REAL_STAGED, annotation_status FROZEN, reviewed_before_inference true, and complete
   the capture provenance. Each clip must match its registered source hash. Annotate
   all four mistake classes and corrections independently of model predictions.
   Mark event_annotation_complete true only after reviewing the full clip. Optional
   frame annotations permit marker recall/placement scoring; omitted annotations
   produce null metrics, not assumed perfect detection.
7. Run python scripts/run_physical_eval.py --annotations data/physical_labels.json.
   It verifies hashes and consent, preserves immutable run folders and reports native
   clip/event outcomes separately from all synthetic and external compatibility runs.
8. For a live demo, open Studio, explicitly allow the camera, start on an empty board,
   make the wrong-fastener error, remove it, place the correct part, then request
   checkpoint. Preserve original and corrected events. No physical fastening/torque
   or intrinsic component identity claim follows from visible tags.

Offline detector timing and source-video onset-to-event delay are separate from
live capture-to-visible-browser latency. The latter remains NOT_MEASURED until a
real capture clock and visible alert clock are instrumented and validated together.
Camera permission, acquisition and public redistribution are separate decisions;
all original staged footage remains local and ignored by Git by default.
"""
    (output / "README.md").write_text(text, encoding="utf-8")
    receipt = {"created_at": dt.datetime.now(dt.timezone.utc).isoformat(), "trials_planned": len(rows),
               "trials_recorded": 0, "trials_evaluated": 0, "camera_opened": False, "recipe_sha256": recipe.sha256}
    (output / "kit_receipt.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    print(f"Prepared {output}: 20 planned trials; 0 recorded; camera not opened.")
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=bootstrap.ROOT / "runtime/physical_kit")
    args = parser.parse_args()
    prepare(args.output)
