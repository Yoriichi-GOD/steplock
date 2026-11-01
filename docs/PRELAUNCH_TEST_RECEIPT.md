# Pre-launch verification receipt

Date: 2026-11-01. Branch: `prelaunch-experience`.
Baseline `day1-final`: `dd056687dcfa4f179519132378137d80d3d21570`, preserved.
Core implementation: `72b0667e0171a946f1d22c203ece05ee43200062`.
Public security/browser implementation: `f2f16a7b5962db1d92281e74ed36f9fe9e32600d`.
This receipt distinguishes local, Linux-container and hosted evidence.

## Executed checks

| Check | Measured outcome | Evidence / scope |
|---|---|---|
| Native backend full regression | 121 passed, 1 dependency deprecation warning, 82.16 s | Includes original engine, calibration, evidence, optional-agent and eight public-boundary tests; licensed research assets exist locally |
| Launcher follow-up | 3 passed, 2.01 s | Public-mode health recognition added after full suite; actual repeated startup reused port 62401 without a duplicate process |
| Frontend regression | 24 passed, 0 failed | Original 22 tests plus public neutral/offline and honest contact/evidence tests |
| Frontend production build | PASS, 6.47 s | TypeScript + Vite; lazy Three.js chunk remains large (1,004.89 kB / 275.49 kB gzip) |
| Public Chromium acceptance | 22 checks PASS | `screenshots/prelaunch/acceptance.json`; actual production build and live backend, not a component mock |
| Original `/app` Chromium acceptance | 9 checks PASS | `screenshots/prelaunch/workbench-acceptance.json`; actual normal/wrong-component replays, all six tabs and source-loss status |
| Frontend alone, no backend | PASS at 1280×720 | `screenshots/prelaunch/frontend-only-acceptance.json`; Vite production preview on port 62403, no request interception; PENDING, disabled run and zero confirmed green steps |
| Linux regression/build/container | PASS | [Verified run](https://github.com/Yoriichi-GOD/steplock/actions/runs/41296194824), source `f2f16a7`; 118 backend passed, 3 research-asset tests explicitly skipped; frontend 24 passed; actual Linux image build and four HTTP inspections |
| AWS API request preparation | ECS offline CLI schema check passed; WAF output-skeleton check blocked | `infra/aws-steplock/validation-receipt.json`; no account or resource API used |
| AWS hosted acceptance | NOT_RUN / NOT_DEPLOYED | Paid deployment was not authorized by the current brief |
| Physical factory / real assembly PASS | NOT_ESTABLISHED | Generated fixtures and software checks do not establish physical performance |

The Linux runner lacks local licensed research assets and did not substitute
synthetic media for those three tests. The native checkout ran them. The first
Linux attempt failed two launcher tests because CI had not created the expected
environment/frontend build; it remains in history. The next run corrected setup
order and passed. Earlier browser overflow at 768 px was fixed and rerun; the
ignored runtime failure record remains available.

## Four engine-backed public examples

| Input | Observed final verdict | Required event observed |
|---|---|---|
| Normal | PASS | CHECKPOINT |
| Wrong Component | HOLD_FOR_REVIEW | WRONG_COMPONENT |
| Wrong Order | HOLD_FOR_REVIEW | ORDER_VIOLATION |
| Correction | PASS | CORRECTED, linked to original WRONG_COMPONENT |

These outcomes were observed in backend tests, actual browser requests and the
Linux container smoke. They were not assigned by the website. Source hashes,
recipe hashes, frame IDs, event timestamps and retained source/overlay frames come
from the existing engine. No evaluator ground truth was modified or used by
inference. Public tests also retrieved original PNG and annotated JPEG evidence
using the correct content types and verified a foreign token receives 404.

## Browser coverage

Chromium 156.0.8078.4, isolated local profile, production build. Desktop hero at
1440×1000; landing/demo width checks at 360, 390, 768, 1280 and 1920; source-loss
at 1280×720; reduced-motion/offline startup at 390×844. No horizontal document
overflow, broken landing image, uncaught public page error or external visual
request was observed. These are desktop-browser viewport checks, not physical
mobile-device testing or a multi-browser accessibility certification.

The browser exercised 3D/2D switching, explode/assemble, wrong-order illustration,
actual WebGL context-loss fallback, reduced-motion 2D, private workspace gate,
four source-video results, retained evidence selection, cross-session denial,
reset/neutral refresh and missing-backend startup. Blocking session polling after
a PASS changed the visible verdict to SOURCE LOST and removed confirmed green
step styling. The original workbench also suppressed its PASS after source loss.

A separate frontend-only production preview was then tested at 1280×720. There
was no backend API on that origin and no browser request interception. The page
showed its unavailable-service notice, neutral PENDING, disabled Run and zero
confirmed green steps. This complements the controlled network-loss checks above.

Paint/navigation timestamps are retained in the acceptance JSON. They describe
this local machine and run, without network/CPU throttling; no Lighthouse score,
mobile frame-rate target or public internet latency is claimed.

## Public boundary and lifecycle coverage

Public tests deny private uploads/camera/recipes/model routes and API docs even
when called directly. They reject arbitrary example IDs, unexpected properties,
foreign Origin, oversized and chunked POST bodies, other-visitor tokens and expired
sessions. They check one-running-session exclusion, retained-session capacity,
persistent rate limits across gateway recreation, deletion of owned evidence,
old orphan cleanup without deleting unrelated directories, narrow health-host
exception, owner-cookie authentication/expiry, HTTPS Secure/HttpOnly/SameSite
cookie behavior, CSP/HSTS and missing contact/secret non-disclosure.

Snapshots and evidence reads share the cleanup lock. One evidence image is copied
before responding, so TTL cleanup cannot remove a deferred response's source file.
SQLite counters are local persistence, not a distributed or hard financial quota.
WAF and hosted proxy/rate behavior remain deployment gates.

## Definition of done against the brief

| Requirement | Status |
|---|---|
| Complete responsive landing, truthful copy, planned roadmap | IMPLEMENTED; browser checked |
| Account-free real engine demo with four scenarios/evidence | VERIFIED on native backend, Chromium and Linux container |
| Procedural 3D, interactive parts, 2D/reduced-motion/context fallback | VERIFIED in Chromium; illustration clearly disclosed |
| Preserve existing workbench/backend/evaluations | VERIFIED by regressions and six-tab `/app` browser run; historical report files untouched |
| Server-side public restriction and bounded temporary data | IMPLEMENTED + TESTED; cloud-edge controls are prepared, not deployed |
| Public email / contact | INTENTIONALLY UNCONFIGURED by founder; no fake submission success |
| Deployment preparation, cost, domain and cleanup instructions | PROVIDED; approval/account-specific/hosted gates explicit |
| Genuine screenshots and provenance | 17 unaltered browser captures with hashes in `screenshots/prelaunch/provenance.json` |
| Existing immutable checkpoint | PRESERVED; ordinary new commits, no rewritten history |

Optional model guidance remains advisory and separate from deterministic findings.
The public demo does not call it. External untagged video recognition, industrial
accuracy, torque/fastening verification, machinery control, and safety certification
are outside what this release has proved.
