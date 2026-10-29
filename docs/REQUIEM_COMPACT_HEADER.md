# Current compact REQUIEM header

The latest user correction replaces the tall576px fixed scene with the supplied
**1691x248 text-free header-ready crop**. The screenshot reference is still never
used in the live interface. Earlier full-height screenshots are historical only.

- Desktop masthead248px: pinned navigation110px, scrolling title area138px.
- Only the logo/navigation/status bar stays in place. The title, crop and body
  move together in `.rq-page-scroll`; page changes reset that scroller.
- The taskbar is translucent over the masthead and darkens after scrolling for
  readable labels over white evidence. It has no outline border.
- Full Celestial artwork continues behind the lower workspace. Black panels stay
  opaque, and the source frame/annotations receive no artwork or filters.
- Side windows now render at140x249px with the original941:1672 aspect ratio,
  rather than tiny76px-wide images in full-height slots. They are hidden below
  1550px to preserve working space. Floral rail corners remain separate.
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
|Scroll| Page scroll355.33px; masthead top-355.33px; taskbar top0px; taskbar darkened |
|Natural pane ratio| Both desktop windows140px wide,249px high; no stretching |
|Normal example| Actual synthetic inspection reached PASS; watermark retained |
|Navigation| Separate Assembly Explorer opens, returning to Studio resets scroll |

Current untouched browser captures: `screenshots/requiem-compact/`. Asset source
and output hashes remain in `frontend/public/assets/steplock-header/manifest.json`.
The current crop is121,648bytes; the existing full body background is308,896bytes.

Changed source scope: `frontend/src/App.tsx`, `frontend/src/theme/requiem.css`,
`frontend/src/theme/theme.test.mjs` and the header asset manifest's usage note.
README, current/historical UI report links, progress notes and current screenshots
are documentation only. The other agent's judging documents are excluded.
