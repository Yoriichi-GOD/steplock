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

The encoded freeze cases also revealed that MJPEG changed the first few decoded
copies (mean grayscale differences approximately 0.09–0.11 after smoothing and
downsampling). Exact pixel hashes therefore allowed the base to confirm, although
the final decision still held and three downstream steps remained unproven. The
four expected checkpoint warnings were only three, reducing event recall.

Protocol v3 adds a conservative near-duplicate gate, selected on those development
clips: grayscale Gaussian 5×5, resize to 240×150, compare against the last accepted
signature. HOLD when mean difference <0.15 AND the fraction of pixels changing by
more than 8 levels is <0.0003. Development normal/recovery exposures showed larger
changes. This remains a heuristic: very clean stationary camera frames may abstain,
and edited or recompressed copies are not cryptographically proven independent.
The exact encoded freeze clip is now a regression; no step may confirm from it.

An initial implementation made every near repeat a hard quality failure. The
existing raw-pixel recovery regression caught an unnecessary final HOLD from one
very small camera movement. We separated spatial usability from independent
temporal support: a near repeat cannot add/clear support; previously supported
evidence remains valid within its existing 1800ms window. Repeated exact bytes
still HOLD immediately. An independent-support gap over 1800ms requires restart.
This prevents codec copies from confirming a step while preserving recent proof.
