# Development-only diagnosis before held-out scoring

The first development run `20261029_055525_293456_dev` remains unchanged. It
processed 16 generated clips / 432 frames: STEPLOCK had 15/16 final statuses,
event TP/FP/FN 28/0/2, and 0/12 false PASS. The recovery clip in transform group 1
ended in HOLD because tag 11 was missed in its final frame; all three methods
held. This was a useful conservative failure, not a reason to weaken PASS.

Diagnosis on that development frame compared current defaults, wider adaptive
threshold windows, no subpixel refinement, threshold constant 3, and more pixels
per cell. Wider windows and constant 3 recovered tag 11; the other two changes
did not. We selected wider windows (max 45, step 4) and kept subpixel refinement,
all temporal support rules, evidence labels and current-visibility requirements.

Protocol v2 records these settings before held-out scoring. No held-out procedure
results were inspected to choose them. First-run artifacts retain v1 configuration
and source hashes. Runtime filenames/labels are never detector inputs.
