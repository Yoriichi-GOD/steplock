# STEPLOCK pre-launch implementation

Baseline: `day1-final` / `dd056687dcfa4f179519132378137d80d3d21570`.
The frozen tag, historical evaluations and original procedure semantics are unchanged.
Development branch: `prelaunch-experience`.

## Architecture audit

The original React 19/Vite frontend was a local workspace at `/`, backed by
FastAPI, OpenCV contrib 4, a temporal recipe engine and per-process sessions.
Four generated fixtures already demonstrate normal, wrong component, wrong order
and correction. Existing source timestamps, observation hashes, recipe hashes,
events and source frames are reused. No ground truth enters inference.

Original host checking accepted localhost only. The static mount did not provide
SPA entries at `/demo` or `/app`. Public uploads, camera ingestion and recipe
editing needed a server boundary. The Dockerfile existed but the Linux daemon
was unavailable. Existing 3D geometry, local art and React Three Fiber/Drei/GSAP
are reused; no proprietary CAD, external font, environment map or new model is
downloaded.

## Routes

- `/`: celestial/industrial pre-launch story and lazy 3D mechanical illustration.
- `/demo`: simplified, account-free generated-example inspection cockpit.
- `/app`: existing full workspace. Public-mode access requires owner login;
  without a configured owner key it stays unavailable. Local mode retains the app.
- `/api/public/*`: restricted public configuration and example sessions.
- `/api/*`: existing private/local API, protected in public mode.

The demo uses the actual detector, procedure engine, checkpoint and evidence
store. Its namespace has separate bounded sessions. It does not invoke Nebius.
The full application's source/evidence/agent contracts remain unchanged.

Contact is intentionally unconfigured at the founder's request. No personal email
was published. The form opens a user-reviewed email only after an authorized
`STEPLOCK_PUBLIC_CONTACT` is configured; it never claims to store/send a message.

## Definition of done

Working direct routes; all four pixel-based examples and evidence retrieval;
cross-visitor access denial; server-enforced public restrictions; bounded data,
expiry and persistent request limits; 3D and 2D; mobile/reduced motion/context-loss
acceptance; stale-PASS suppression; existing regression suite; production build;
documented Docker/hosting checks and any genuine blockers. Paid AWS resources,
domain purchase and publication are outside this implementation authorization.

Progress receipts and exact remaining checks are recorded in
`PRELAUNCH_TEST_RECEIPT.md` and `DEPLOYMENT_READINESS.md` as they complete.
