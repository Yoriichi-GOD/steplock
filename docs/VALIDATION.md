# Validation receipts

Build date: 29 October 2026. Commands below ran on the local Windows environment;
they do not establish physical-camera or industrial validation.

| Check | Actual result / scope |
|---|---|
| Python regression | 45 passed; one upstream Starlette/httpx deprecation warning |
| Marker generation | 10 IDs × four orientations decode; perspective tested |
| Frontend production build | TypeScript + Vite passed |
| Headless production replay | normal example → PASS, 30 frames, saved hashes/events |
| API integration | upload, replay, final check, exports, tokens, isolation, invalid media/path |
| Privacy/local boundary | explicit real-input consent, local Host/origin checks, no camera auto-start |
| Recipe persistence | new versions survive restart; old session recipe hash unchanged |
| Temporal/correction | duplicates, codec copies, occlusion, backward time, midassembly, wrong-zone/OUTSIDE recovery |
| First scored synthetic run | 32 clips / 864 frames; committed prediction source c14e7f0, retained unchanged |
| Final scored verification | 32 clips / 864 frames; committed prediction source 0a00d99; 32/32 final statuses, TP/FP/FN 60/0/0, false PASS 0/24 |
| 3D state adapter | 10/10 production-adapter regressions, independently rerun by engine owner |
| Synthetic stress grid | 14/14 designed safety gates passed; separate from accuracy |
| Staged-real / physical camera | NOT_PROVIDED / NOT_TESTED |
| True capture-to-visible latency | NOT_MEASURED |

Browser checks before browser access was disabled in Work settings:

- Actual normal replay reached PASS; wrong component reached HOLD; screenshots saved.
- Stopping the owned backend changed stale browser PASS to SOURCE LOST, disabled
  decision controls and preserved prior visual evidence as historical evidence.
- Canonical scratch install launched successfully with backend health on a free
  local port. A 1440×900 DOM geometry check found no horizontal overflow and all
  source/checkpoint/acknowledgement controls in the viewport.
- The coordinated UI chat reports tested mesh selection/orbit, explode/reassemble,
  read-only recipe animation, actual wrong-part red state, evidence links, correction,
  context-loss 2D fallback, one-click graphics recovery, offline amber state, and
  390px reduced-motion layout without horizontal overflow. Exact evidence and
  boundaries are in `UI_COORDINATION.md` and `ASSEMBLY_VIEWER.md`.

Fresh normal/wrong-component/correction API replays and direct final-frame image
inspection verified the corrected overlay wording. A near-repeat frame says
NO NEW TEMPORAL SUPPORT rather than issuing an independent HOLD. The UI adapter
was also checked against these actual snapshots, including disconnected states.

Pending browser gates: explicit 1280×720 view, startup with WebGL entirely unavailable,
and a refreshed final canonical integrated browser screenshot. Browser access became
disabled in Work settings during testing;
do not describe these unperformed follow-ups as passing. Existing screenshots
retain their original context; `assembly-corrected-inspection.jpg` records the
old overlay contradiction and is not a final approval screenshot.

## Finalization

The original test run and earlier development failures stay immutable. The final
separate evaluation is `benchmarks/runs/20261029_065156_263419_test/`: STEPLOCK
precision/recall/F1 1/1/1, 16/16 timed mistakes, 4/4 corrections; vision p50/p95
17.4/23.5ms; offline shared throughput 43.4fps. Marker recall 5208/5208 visible
opportunities, zone localization 1752/1752; occluded opportunities remain separately
reported. Generated cases do not establish physical generalization.

Fresh setup from the canonical scratch checkout completed with pinned Python
dependencies and `npm ci`, frontend build, loopback launch and a healthy API. The
integrated 3D rebuild and final source audit are recorded below when complete.

Final canonical integration, 29 October 2026: pinned Python environment, clean
`npm ci`, integrated TypeScript/Vite build, 45 Python tests and 10 frontend tests
passed from `C:/Users/nrgen/.codex/scratch/steplock`. The actual local app returned
HTTP 200 and health `ok`. An actual HTTP correction replay analyzed 42 generated
frames, ended PASS with 4/4 placements and exactly one CORRECTED event; authenticated
JSON and HTML exports succeeded. Camera remained inactive. The printable HTML
summary selects at most six boundary/finding events and directs readers to the
complete JSON ledger; physical print pagination was not visually verified.

The canonical checkout has a separately supplied, untracked `ui/` asset pack and
brief added during finalization. These files are preserved and excluded from this
core release. The user's separately requested appearance update remains owned by
the UI chat. No raw reference pack or full private specification was published.
Tracked release files are synchronized; no claim of a completely empty worktree
is made while that user-supplied material is present.
The latest receipt may be in the following commit because a Git commit cannot
contain its own final hash without changing that hash.
