# README screenshot clarity

The previous README linked `screenshots/requiem-glass/studio-1691.png`. Inspecting
its bytes showed JPEG/JFIF encoding despite the `.png` extension:1691x930,
135,680bytes. The browser screenshot helper returns compressed JPEG. Renaming
those bytes to `.png` did not make them lossless, and GitHub's reduced display
size made the small dashboard text harder to read. Historical captures are kept.

The replacements are genuine PNG captures obtained from Chrome's
`Page.captureScreenshot` with `format:png`, through the existing browser tool.
They were captured29October2026 from the actual local app at
`http://127.0.0.1:62327/`, application revision7352088. Later repository changes
before this capture were documentation only.

- `screenshots/readme/studio-native.png`:1920x1080 viewport capture, default
  1280x720 CSS viewport at device pixel ratio1.5. No viewport enlargement or image
  upscaling was used to manufacture resolution.
- `screenshots/readme/inspection-native.png`:1920x1080 native viewport capture
  after ordinary scrolling. It retains the source's synthetic watermark and all
  four step states, advisory and evidence controls. The transparent pinned
  navigation visibly passes over the toolbar, reflecting the actual interface.

Both images show the same actual `normal` synthetic fixture session, with PASS,
four confirmed placements and zero open findings. Under concurrent local work,
25frames were analyzed and5were intentionally dropped; FRAME30 is the source-frame
index. This capture is a UI example, not a throughput or accuracy benchmark.

The files were saved directly from the browser's base64 PNG bytes, with no image
sharpening, retouching, resampling, reconstructed text or AI-generated UI. The
scenery is intentionally blurred only behind the glass surfaces; source frames
and foreground labels retain their actual rendering. No external dataset pixels,
camera footage or credentials appear in these public captures.

README keeps a clickable native-resolution original and an expandable inspection
detail. A narrow README still scales a whole dashboard down, so the original is
the useful path for reading the smallest labels.

This correction changes documentation and screenshots only. No live UI styles,
API, model, engine, recipe, benchmark or launch behavior changed.
