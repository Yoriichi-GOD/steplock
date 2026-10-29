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

- 13:45:45 IST corrective implementation commit:
  `99cbb685a16e5f331dc5772c0659cbb4de77aea0`.
- Verified push receipt: `4c0385d..99cbb68 main -> main`.
- `git ls-remote origin refs/heads/main` returned that exact SHA after the push.
  The following documentation-only receipt commit does not change runtime code.

## Full Celestial header revision (29 October, 14:13 IST onward)

- User asked for black opaque surfaces, borderless panels/transparent header,
  full logo, a larger Procedure Studio title, visible side ornaments, fixed art
  and body-only scrolling, with Assembly Explorer as its own real navigation tab.
- The user explicitly chose the full uncropped Celestial master in a taller
  proportional header, superseding the earlier 248px crop. Full provenance and
  breakpoint measurements: `docs/REQUIEM_HEADER_IMPLEMENTATION.md`.
- Work paused for a user-requested Codex restart when browser access reported
  disabled. Resumed14:24; real screenshots and interaction checks completed.
- Frontend20/20, build passed; original backend45/45 passed. Core teammate's
  independent validation tooling checkpoint `c605b6a` was preserved and excluded
  from the UI allowlist.
- Browser verified1691x930,1440x900,1280x720,1024x768,390x844,320x760; all six
  tabs on mobile, no horizontal overflow, toolbar flush with header, actual
  PASS/HOLD, original/overlay/scrub/checkpoint, HTML report, consent gates,
  real stopped-backend SOURCE LOST and fresh frontend-only ENGINE OFFLINE.
- Fixed three measured issues before publication: body grid overflow from an
  inherited auto margin, logo expanding the nav row, and tab scroll retention.
- 14:49:02 IST implementation commit:
  `df9b28528b3df9fc90851c9f5028e7e6df3030f6`.
- Push receipt: `c605b6a..df9b285 main -> main`; independently verified
  `git ls-remote origin refs/heads/main` returned that exact SHA.
- Only19 UI/source/art/doc/screenshot files were included. Teammate validation
  scripts, reports, tests, datasets and the shared README were excluded.

## Compact masthead correction (29 October,14:59 IST onward)

- User explicitly switched back to the1691x248 ZIP crop and clarified that only
  the taskbar should stay fixed; title/art should scroll. Lower-page scenery and
  natural pane proportions replace the empty margins/tiny windows.
- Current source/measurements/screenshots: `docs/REQUIEM_COMPACT_HEADER.md` and
  `screenshots/requiem-compact/`. Older full-height screenshots are historical.
-20 frontend checks and build passed; browser proved248px desktop masthead,
  toolbar boundary, only-nav pinning, natural140x249 panes and normal PASS.
- No core changes; other agent's judging docs excluded from the UI checkpoint.
