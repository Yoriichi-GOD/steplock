# Rounded neutral glass panels

Body windows and the source toolbar have18px corners and a neutral translucent
surface: rgba(10,10,10,0.48), with20px backdrop blur. There is no blue, teal or
other colored overlay in the glass. The scenery supplies the colors behind it.
Panel headings and camera controls use a light neutral shadow layer. Secondary
text is brighter inside the panels for readability. Existing status accents and
floral ornaments are retained.

Only backgrounds behind each panel are blurred. Text, source imagery and evidence
annotations remain unfiltered. The source letterbox is transparent; fullscreen
uses an opaque neutral background. Browsers without backdrop-filter support get
a neutral near-opaque fallback (implemented; not separately browser-tested).
The header remains completely transparent, and only navigation stays pinned.

## Verification

- 20 frontend checks and production build passed. The evidence test now permits
  transparent letterbox backgrounds while still prohibiting filters, opacity,
  transforms and artwork on the evidence layer.
- Actual browser at62327 measured18px corners,20px backdrop blur, neutral equal-RGB
  panel color, and no blur/filter/opacity change on the source image.
- Normal synthetic inspection reached PASS with30 analyzed frames. Original and
  annotated source toggles worked; Evidence Explorer and return navigation worked.
- 1691x930,1280x720 and390x844: no horizontal page/scroller overflow. Phone glass
  corners and source controls were inspected visually.
- Current unmodified screenshots: `screenshots/requiem-glass/` (synthetic evidence
  only). Existing solid-palette contrast checks are reference-color checks;
  they do not certify contrast over every possible scenic backdrop.

Runtime change is CSS only. No API, vision, recipe, source transport or launcher
behavior changed. The preceding65/65 backend receipt was not rerun or relabeled
for this presentation-only correction. Judging documents and raw media remain
excluded from the UI checkpoint.
