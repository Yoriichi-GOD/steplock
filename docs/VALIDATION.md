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
| First scored synthetic run | 32 clips / 864 frames; exact committed prediction source c14e7f0 |
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

Pending final browser gates: refreshed frame-overlay wording, explicit 1280×720
view, startup with WebGL entirely unavailable, and final canonical integrated
build screenshot. Browser access became disabled in Work settings during testing;
do not describe these unperformed follow-ups as passing. Existing screenshots
retain their original context; `assembly-corrected-inspection.jpg` records the
old overlay contradiction and is not a final approval screenshot.

## Finalization

The original test run and earlier development failures stay immutable. A final
separate evaluation and repository audit will be linked here after completion.
The latest receipt may be in the following commit because a Git commit cannot
contain its own final hash without changing that hash.
