# REQUIEM progress and publication receipts

All times are Asia/Kolkata (IST), 29 October 2026. This is the team's requested
45-minute working checkpoint cadence, not an independently verified organizer rule.
No timestamps or history were rewritten and no force push was used.

## Baseline and restart

- Baseline `main`: `df5d8a6ec5c1c5900cf8af93f1d87cbe405cc9ea`, clean tracked tree.
- 12:56 IST: began brief/ZIP inspection; baseline frontend checks passed 16/16.
- Work paused at the user's request to restart Codex because the browser tool
  contradicted the enabled setting. No REQUIEM source edits existed at that pause.
- 13:08 IST: resumed. Browser access now worked. The old preview had stopped.
  Used the normal launcher, which selected port 55520; saved an actual baseline
  screenshot under ignored `runtime/requiem-inspection/baseline.png`.

## Published integration checkpoint

- 13:31:53 IST commit: `4c0385d2edefd30693807979d23103fbf7548288`.
- Push receipt: `df5d8a6..4c0385d main -> main` at
  `https://github.com/Yoriichi-GOD/steplock.git`.
- `git ls-remote origin refs/heads/main` returned exactly
  `4c0385d2edefd30693807979d23103fbf7548288` after the push.

- Replaced only the rejected theme layer, preserving all core history and APIs.
- Seven optimized art files: 796,298 bytes; source/output provenance in manifest.
- 18 frontend tests and 45 existing backend tests passed; production build passed.
- Actual browser runs: normal PASS, wrong-component HOLD, unchanged HOLD after
  acknowledgement, evidence navigation, scrub/overlay, checkpoint, JSON/HTML
  downloads, real synthetic upload, network interruption, missing art and failed
  evidence fallback. Camera rejection was injected; no physical camera used.
- Responsive screenshots: `screenshots/requiem/`; screenshot files are untouched.

## Original-folder handoff

- Fast-forwarded the original `C:/Users/nrgen/.codex/scratch/steplock` checkout;
  its 18 frontend tests and production build also passed.
- Preserved the untracked `ui/` source folder and its ZIP, whose SHA-256 still
  matches the recorded input. Preserved the earlier saved-work stash
  `01bd40e74be4b5826bdf6a31f52f2d7497cbda5d`.
- Normal launcher in the original checkout selected `http://127.0.0.1:61795`.
  Health returned OpenCV 4.14.0, ArUco available, advisory-only, camera inactive.
  All seven served image bodies matched their production manifest hashes.
- A separate build with base `/steplock/` passed; CSS art URLs, favicon and
  client asset base were checked for that prefix. The normal production build
  remained at its ordinary base.
- Additional browser checks: 1920px separate arch, all five pages at 390px with
  no page overflow, camera rejection fallback, existing 2D/3D explorer controls,
  and actual Stop source. Temporary fault injection was removed.
- The final documentation commit records these real receipts; its SHA is visible
  in normal Git history rather than a self-referential placeholder.

## Final responsive correction

- A fresh offline-startup browser check found PENDING wrapping onto a single
  trailing letter at the narrow-laptop breakpoint. Reduced verdict typography
  there and preserved normal word wrapping. Rebuild and 18 frontend checks
  passed. At 1280px, the actual browser measured PENDING at 40px with height 48px
  and line-height 48px, confirming a single line with no page overflow. No backend
  behavior changed.
