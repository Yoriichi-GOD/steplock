# Current compact REQUIEM header

The latest user correction replaces the tall576px fixed scene with the supplied
**1691x248 text-free header-ready crop**. The screenshot reference is still never
used in the live interface. Earlier full-height screenshots are historical only.

- Desktop masthead248px: pinned navigation110px, scrolling title area138px.
- Only the logo/navigation/status bar stays in place. The title, crop and body
  move together in `.rq-page-scroll`; page changes reset that scroller.
- The taskbar is fully transparent, including after scrolling: no fill, shadow,
  blur or outline border. Individual buttons retain their own functional styling.
- Full Celestial artwork continues behind the lower workspace. Black panels stay
  opaque, and the source frame/annotations receive no artwork or filters.
- Both decorative side windows and their layout columns are removed. The Studio
  grid fills the workspace content width; the camera receives the reclaimed
  space. Floral rail corners and the lower-page background remain.
- Phone layouts retain a280px masthead to fit the scrolling navigation row,
  title and both real action buttons. All original tabs plus Assembly Explorer,
  Setup Guide, conditional HTML Report, engine state and advisory labels remain.

## Verification

Production build and20 frontend checks passed. No backend, API, inference,
benchmark or dataset files were changed by this revision. The preceding combined
repository backend receipt remains58/58; it was not relabeled as a new run here.

Actual browser checks used the built app at an auto-selected temporary port:

| View | Measurement / outcome |
| --- | --- |
|1691x930| Masthead248px; toolbar starts at248px; nav110px; no horizontal overflow |
|1280x720| Masthead248px; toolbar starts at248px; no horizontal overflow |
|1024x768| Source-first tablet layout retained; breadcrumb clearance rechecked |
|390x844 and320x760| Adaptive280px masthead; no horizontal page/scroller overflow |
|Scroll| Page scroll379.33px; masthead top-379.33px; taskbar top0px; background rgba(0,0,0,0) |
|Expanded desktop grid| Content1591.98px; camera1013.98px; zero decorative side windows |
|Normal example| Actual synthetic inspection reached PASS; watermark retained |
|Navigation| Separate Assembly Explorer opens, returning to Studio resets scroll |

Current untouched browser captures: `screenshots/requiem-wide/`. Earlier captures
in `screenshots/requiem-compact/` retain the superseded tint and window panes.
Asset source
and output hashes remain in `frontend/public/assets/steplock-header/manifest.json`.
The current crop is121,648bytes; the existing full body background is308,896bytes.

Latest correction source scope: `frontend/src/App.tsx`,
`frontend/src/pages/Studio.tsx` and `frontend/src/theme/requiem.css`. The only
React changes remove the scroll tint state and the two decorative image nodes
and their wrapper. All inspection callbacks are retained. No new backend tests
were run for this visual-only correction. The other agent's judging documents
are excluded from this UI checkpoint.

The transparent pinned navigation can pass over light source evidence after
scrolling. This is the user's explicit request; no darkening overlay is applied.
