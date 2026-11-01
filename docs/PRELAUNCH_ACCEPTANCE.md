# Industrial Requiem acceptance

Date: 2026-11-01. Branch: `industrial-requiem`.
Starting pre-launch commit: `cb7c84bcf88599007ddb36f4e10740b9dcd3bd74`.
First cinematic checkpoint: `872e478f3f99d3b0649b151a4c9f894d801948c2`.
Frozen `day1-final` still targets `dd056687dcfa4f179519132378137d80d3d21570`.
The final source-input hashes and 25 unaltered browser captures accompany this receipt
under `screenshots/industrial/`. Earlier pre-launch and benchmark reports are retained.

## Definition of Done

| Requirement | Outcome |
|---|---|
| Factory-origin story central, respectful to operators | Seven acts implemented; factory is explicitly inspiration, not a customer/pilot |
| Coherent mechanical story | Shared original geometry, one scene/playhead through Acts I–IV, factory stations, early-cover illustration, late-feedback travel, stillness and rewind |
| Advanced motion has a purpose | ScrollTrigger, SplitText, Flip, MotionPath, CustomEase and `@gsap/react`; one Lenis ticker on appropriate desktop configurations |
| Intentional typography | Four self-hosted families, Latin weights only, local OFL notices; no remote fonts |
| Functional prototype | Four live engine-backed generated examples with current source/steps/verdict and retained frame inspection |
| Genuine evidence detail | Actual API-captured wrong-component event/source/overlay/hashes; retained-case label; keyboard comparison and expandable record |
| 2D/accessibility/failure path | SVG story, component buttons, native mobile/reduced motion, WebGL-loss/startup fallback, pause and responsive controller cleanup |
| Existing app preserved | Original six-tab workbench tested; shared geometry defaults preserve its status adapter; bounded heartbeat fixes a reproduced stale-PASS case |
| Public boundary | Existing allowlist, tokens, limits, cleanup and owner gate retained; server regression passed |
| Deployment preparation | Same isolated one-container AWS candidate, costs, host/HTTPS/domain/teardown instructions; no paid cloud change |
| Contact | Intentionally unconfigured; no invented address, discarded waitlist or fake send confirmation |

## Executed commands and environments

Windows 11, existing Python 3.14/OpenCV 4.14 environment, Node/npm and Vite production
build. Isolated Playwright Chromium **156.0.8078.4**, no personal browser profile.
Tests use loopback-only servers and runtime directories outside OneDrive.

```powershell
npm --prefix frontend test
npm --prefix frontend run build
python -m pytest backend/tests -q
python scripts/smoke_public_demo.py --origin http://127.0.0.1:62401
node scripts/industrial_browser_qa.cjs
node scripts/prelaunch_workbench_qa.cjs
node scripts/prelaunch_startup_qa.cjs
```

The shell's `python` in these examples means the installed STEPLOCK environment;
this session used the existing `.venv/Scripts/python.exe`. Actual pytest temporary
data was under `%TEMP%/steplock-industrial-regression` rather than synced storage.

- **26 frontend tests passed**, including all prior tests, bounded/presentation-only
  story poses, a true stillness interval and actual retained source/hash integrity.
- **122 backend tests passed in 83.20 seconds**, with one Starlette/httpx deprecation
  warning. Inspection engine, security, recipe, evidence and optional-agent tests ran.
  No engine, recipe, ground-truth or benchmark file changed in this release.
- **Production build passed.** The heavy lazy graphics dependency chunk remains
  about 1,003 kB raw / 275 kB gzip; it is not needed for the SVG path or public demo.
  Gzip size is a build estimate, not proof that a future AWS endpoint compresses it.
- **35 cinematic/public browser checks passed**: all four actual scenarios, source
  frames, record expansion/comparison, 3D continuity, keyboard component selection,
  explode, actual graphics-context loss, unsupported WebGL startup, responsive
  Lenis removal/recreation, pause/resume, neutral refresh and stalled/failed requests.
- **10 original-workbench browser checks passed**: actual normal/wrong-component
  runs, source frames, all six tabs, held-request timeout and source-loss behavior.
- **Frontend-only startup passed at 1280×720**, without API interception or a backend
  on that origin: clear unavailable state, PENDING, disabled Run and zero green steps.

Exact assertion records, origins, timings and browser versions are in the adjacent
JSON captures. Port 62401 is the user preview, 62402 the isolated private workbench,
62403 the frontend-only server, and 62404 the clean final public QA instance.
They serve the same production build. Test-only servers are stopped after capture.

## Outcomes from actual generated-pixel inspections

| Scenario | Observed final verdict | Visible replay completion | Event/evidence requirement |
|---|---|---|---|
| Normal | PASS | 6,060 ms | Final checkpoint and confirmed procedure |
| Wrong Component | HOLD_FOR_REVIEW | 6,127 ms | WRONG_COMPONENT with retained source frame |
| Wrong Order | HOLD_FOR_REVIEW | 6,144 ms | ORDER_VIOLATION |
| Correction | PASS | 8,460 ms | New CORRECTED event retaining the prior finding/link |

These are actual software executions over generated examples, not physical-world
accuracy. The optional model is not invoked. A foreign visitor token receives 404.
The browser receipt measures Run-click to visible replay completion for each clip;
that includes replay pacing/network/UI polling and is **not** factory alert latency.
The UI's vision p95 comes directly from the current session's measured detector
times and is explicitly labeled separately from end-to-end latency.

## Failure cases found and fixed

1. Initial mobile illustration overlapped the heading. A dedicated visual band and
   readable text stack replaced the overlapping composition.
2. Deliberate 3D → 2D disposal was mistaken for a WebGL crash. Context listeners now
   detach before normal disposal; genuine connected-context loss still selects SVG.
3. The opposing text reveal extended the 360-pixel document to 398 pixels before it
   entered view. The reveal now clips inside its own composition; body overflow is
   not hidden to disguise the problem. All checked widths fit afterward.
4. The original app retained PASS while a request stayed open. This was reproduced
   with one held request and PASS still visible after four seconds. Public and
   private session polling now abort an unresponsive heartbeat after 2,500 ms,
   suppress the current PASS, and recover after a successful fresh poll. The public
   demo also clears current green step styling while disconnected.
5. Responsive smooth-scroll setup originally survived a desktop-to-mobile resize.
   Its ownership now lives inside the same matchMedia lifecycle and is tested.

Earlier failure JSON remains in ignored runtime data. The final receipt reports
passing checks only after actual reruns; Git history was not rewritten to hide failures, and these are not described as
successful first runs.

## Performance observations and limits

Landing/demo widths: **360, 390, 768, 1280, 1440 and 1920**. The private workbench
and disconnected case were checked at **1280×720**. Mobile is browser/device
emulation with touch/reduced-motion checks, not a physical phone test.

The browser JSON retains first paint/contentful paint, layout shifts, resource
sizes and a 90-sample animation-frame interval profile. These are local,
unthrottled, machine-specific observations; cached resources can report zero
transferred bytes. Do not advertise those as public internet latency or a
Lighthouse score. No stable 60-fps, physical mobile GPU or cross-browser claim is made.
The final isolated 90-sample profile recorded 17 ms median and 63 ms p95 animation-
frame intervals, with 30 reported draw calls and 55 geometries. These intervals
still have a long tail. The first parallel profiling run had longer tails, so final sampling is
isolated and the factory scene's DPR is capped at 1.25. This bounds cost; it is not
proof that every device sustains the same performance.

The scene reports bounded CPU-side render submission samples, draw calls and
geometry count. Time between demand frames is not used as GPU render time because
it includes idle time. CPU submission cost is also not a GPU timer-query benchmark.
Mobile/reduced motion requests no graphics scene chunk in the verified run. A
performance-based simpler mode, explicit 2D and failure fallback remain available.

## Linux and hosting

The first cinematic checkpoint passed Ubuntu GitHub Actions: frontend regression,
production build, backend regression, Linux Docker build and actual four-scenario
container HTTP smoke. [Run 41306857849](https://github.com/Yoriichi-GOD/steplock/actions/runs/41306857849).
The run's exact source commit is recorded in its metadata. Final follow-up source
is pushed normally and its current Linux check is available in
[branch Actions](https://github.com/Yoriichi-GOD/steplock/actions?query=branch%3Aindustrial-requiem).

Local Docker Desktop's existing inference-socket initialization problem was left
untouched. No local image build is claimed. AWS account preflight, actual ECR image
publication, hosted HTTPS/browser acceptance, WAF enforcement and deployment remain
**NOT_RUN / NOT_DEPLOYED** for this release. Existing offline WAF CLI skeleton
validation remains blocked by its output-stub ARN issue, as previously documented.

See `DEPLOYMENT_READINESS.md` and `infra/aws-steplock/README.md` for the isolated
resource plan, cost assumptions, approved-deployment gates, domain and teardown.
No REFLEX resource, secret, checkpoint or historical evaluation was changed.
