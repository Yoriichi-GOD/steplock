# Mechanical scene architecture

`MechanicalPart.tsx` holds the existing base plate, spacer, cover, fastener,
bevels, holes and thread geometry. The original `AssemblyScene` reuses it without
changing its status adapter or default material behavior. The marketing scene
adds an `industrial` finish while preserving that geometry. No proprietary CAD,
downloaded environment map or reconstruction claim is introduced.

`FactoryScene.tsx` is a separate lazy scene using the same parts. Its procedural
conveyor has 26 instanced rollers, thin rails, three tooling frames and overhead
lights. Shared scalar pose values move the group between stations, vary camera
framing, separate components, highlight the illustrative cover and isolate it.
It uses one demand-rendered Canvas throughout Acts I–IV.

## Boundaries

| Layer | Source of truth | Authority |
|---|---|---|
| Geometry / material | Shared procedural part definitions | Illustration only |
| Marketing pose | `storyPose(progress)` from ScrollTrigger | Story composition only |
| Manual interaction | Selection, explode override and optional orbit | Presentation only |
| Full-app illustration | Existing `deriveAssemblyParts(steps, session, connected)` | Reflects backend snapshots conservatively |
| Public inspection | Existing authenticated session snapshots and source-frame endpoints | Deterministic engine owns current advisory |
| Retained marketing case | Actual API capture in `assets/industrial/evidence-case.json` | Historical generated-example finding, explicitly not live |

The marketing model never receives a session or writes a decision. Its pose type
does not contain status, PASS or findings. The retained case is separate from the
illustrative diagnostic. Current demo decisions cannot be overridden by animation.

## Rendering and failure behavior

WebGL is lazy and desktop-first. Mobile, reduced motion, data-saver or low reported
CPU concurrency default to SVG. Canvas uses DPR 1–1.25, one environment capture,
bounded shadow maps, fog and physically based materials. GSAP invalidates the
demand loop only while the pose changes; no idle RAF is required. Orbit controls
invalidate during direct interaction and do not own scroll or wheel zoom.

Resources created by Fiber are disposed on unmount; custom per-part materials are
explicitly disposed. Context loss is handled at renderer creation, before the
world's later effects. Rendering failure selects `FactoryDiagram`, which keeps
the same mechanical story with SVG part transforms and station labels.

The renderer collects 90 bounded samples of CPU-side render submission time. A
mean over 65 ms selects the simpler path. Time between demand frames is excluded
because it includes idle time. This is an adaptive UI threshold, not a GPU timing
measurement or a measured device guarantee. WebGL diagnostics expose
only draw-call/geometry counts on the local canvas element. No analytics, user
video or personal information is collected.

`FactoryDiagram` is independently designed SVG with a dimensional grid, metal
gradients, component labels and isolation/travel transforms. It is not a screenshot
of the WebGL scene. Its keyboard component controls and explode action remain
usable when WebGL is unavailable. The functional demo never depends on WebGL.
