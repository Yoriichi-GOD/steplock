# Stable local preview and pinned real recording

The default address is **http://127.0.0.1:62327/**. Run `python scripts/dev.py`
from the repository, or double-click **Start STEPLOCK.cmd** on Windows to launch
and open it. First setup remains `python scripts/dev.py --setup`. Keep the server
terminal open. Restarting Codex does not require selecting a new port.

A repeat launch recognizes the existing STEPLOCK health endpoint and returns the
same address without creating a second server. If another app occupies that
port, startup stops with a clear error and never picks a replacement address.
No process is killed to reclaim a port. Explicit CLI/environment overrides remain
available for development; `--port 0` means a deliberately temporary test server.

Only navigation sticks while scrolling. The logo and connection/advisory labels
belong to the scrolling masthead. Navigation stays transparent and interactive.
Desktop masthead remains248px; phone masthead remains280px. The expanded Studio
grid, source pixels and lower-page background are retained.

## Real video

**Real video** is a persistent button beside **Run example** when the local
licensed media is present. It runs the existing replay/session/evidence pipeline;
it never opens a camera and does not start automatically on page load. Generated
tests remain available through their own selector and **Run example** button.

The pinned source is a12-second excerpt of IMPACT v1.1 real reassembly video
`AL07EJ17_Reassembly_A_002_front`, source55..67seconds, sampled at5Hz and resized
to640x360 with MJPEG re-encoding:60 actual frames,1,378,890bytes.

- Original source SHA-256:
  `42e8c9100e733c32c2948cf8665790d8431c25539f7cd5162e67e8e44d305faf`.
- Derived excerpt SHA-256:
  `e3494ad487d458923b71e4bb265ff5ab2435f416ceab252cc6aff9cc2a8ea8a6`.
- Local media and receipt:
  `data/external/impact_v1_1/presentation_excerpt/` (ignored, never committed).
- Attribution: Wen et al., [IMPACT](https://github.com/Kratos-Wen/IMPACT).
  Dataset license: [CC BY-NC-SA4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).
  Dataset frames and browser captures containing them remain local, outside the
  code's MIT distribution.

The visible badge is **REAL VIDEO · UNTAGGED**. Source metadata and exports retain
`EXTERNAL_PHYSICAL_UNTAGGED`, `tagged_fixture:false`, attribution, license and
derivation. The existing transport enum is `REPLAY_TAGGED`; that enum does not
claim tags exist in these pixels. No recipe, detector, verdict rule or architecture
was changed. No procedure checkpoint is requested automatically for this clip.

Without STEPLOCK's fixture anchors, the correct advisory is
**CALIBRATION REQUIRED**, never an unsupported PASS. Native assembly mistake
accuracy remains unscored. Use a consented recording of the printed tagged kit
to demonstrate actual four-part procedure confirmation on physical footage.

Missing or changed bytes make the preset unavailable. The UI hides its button;
direct requests fail explicitly. The clip is never replaced with generated media,
and the backend accepts no client-provided filesystem path for this preset.

## Verification

- Frontend20/20 checks and production build passed.
- Backend65/65 passed, including actual60-frame real replay, original/source
  hash checks, provenance export, missing/corrupt media, consent/source labeling,
  fixed-port reuse and unrelated-port conflict behavior.
- The repeat launcher returned62327 with no second server. No camera started.
- Actual browser at the same62327 address: real replay finished with60 analyzed
  frames, no checkpoint requested, one QUALITY_HOLD event, CALIBRATION_REQUIRED;
  JSON download retained the source hash and untagged population.
- Normal example after the real replay still reached PASS with30 frames and the
  synthetic watermark. Evidence Explorer and the phone's last Demo Kit tab opened
  correctly; returning to Studio reset scroll.
- At1691x930: toolbar top248px; scroll379.33px moved logo top to-379.33px while
  navigation stayed at0px and transparent. At390x844: toolbar top280px; navigation
  begins at64px and sticks at0px after the logo row scrolls away (46px tall).
- No horizontal page/scroller overflow at1691,1280,390 or320px widths. Browser
  inspection found an inherited110px phone min-height; overriding it to46px fixed
  the measured64px gap before publication.
- Public screenshots in `screenshots/requiem-stable/` contain only generated
  test evidence. Real-footage browser proof remains local in
  `runtime/qa/stable-real/`, outside Git.

The existing Starlette TestClient deprecation and optional3D chunk-size warning
remain; neither blocks these checks. Frozen benchmarks and judging documents
are unchanged by this follow-up.
