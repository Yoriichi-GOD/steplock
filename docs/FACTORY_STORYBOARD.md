# The Industrial Requiem: storyboard

The founder's account of a friend's family factory is the inspiration. It is not
a customer testimonial, completed pilot or measurement of waste. No factory name,
worker likeness, quotation, photograph or financial result has been invented.
The problem is delayed procedural feedback, not operator intelligence or effort.

The first four acts share one pinned mechanical scene. Five scrolling text scenes
include the deliberate pause within Act III. A single normalized playhead drives
camera, assembly separation, station travel, lighting and isolation. Desktop uses
ScrollTrigger pinning; tablet/mobile use native scrolling and a sticky SVG stage.
The rest of the page makes a visible handoff to actual application evidence.

| Act | Exact principal copy | Composition and progression | Trigger / fallback |
|---|---|---|---|
| I — The factory | “Quality shouldn’t begin at the end.” | Assembly/conveyor/three tooling frames emerge against graphite. Origin copy describes the friend's family factory. “Experience the problem” jumps to Act II; “Try the prototype” goes straight to software. | Playhead 0–0.20; masked SplitText lines and brief blur-to-sharp eyebrow. SVG factory is present before lazy WebGL. |
| II — The knowledge gap | “The task. The procedure. The space between.” / “The operator knows the task.” / “The supervisor knows the procedure.” | Opposing-direction sentences, dependency line and amber cover. The cover descends while the spacer remains above it, illustrating an early placement. | 0.20–0.40; scroll-scrubbed relative part positions. Equivalent SVG transforms and readable copy in 2D. |
| III — Late feedback | “The mistake happened here. Noticed much later.” | Same object travels along the workstation line. Assembly → next operation → inspection. SVG path/dot traces the gap. Additional work, reinspection, possible rework and material consumption are potential consequences, not measured losses. | 0.40–0.65; technical path drawn by stroke length and MotionPath. Native/reduced motion retains labeled stations. |
| III — Stillness | “What if the warning came earlier?” | Factory, grid and other parts recede. One amber cover remains. “Before the next operation. While there’s still a simple next step.” | Pose is identical at 0.65–0.73. No moving text or looping object during this interval. SVG isolates the same part. |
| IV — The idea | “Catch the wrong move before the next step.” | Rewind station travel, inspect the separated assembly, then resolve its illustrative order. Compact panel says “PROPOSED WORKFLOW / ILLUSTRATION” and “Cover depends on spacer.” | 0.75–1.00. Clean technical lighting replaces factory context. No PASS or detector event is assigned by this scene. |
| V — The prototype | “We didn’t stop at the idea.” / “Here’s what we’ve built so far.” | Authentic prior application capture in a technical viewport. Perspective settles as the visitor approaches. “Try STEPLOCK yourself” navigates immediately to `/demo`. | Native section after the shared scene. Source screenshot retains its existing provenance. No navigation animation delays usability. |
| VI — Evidence and limits | “A prototype you can inspect.” | Actual retained wrong-component frame/overlay comparison. Expand the technical record to read the genuine event, capture status, source time and hashes. Method and limitations are adjacent. | GSAP Flip expands DOM layout after React commits. Keyboard range control compares source/overlay. No invented or live-looking telemetry. Reduced motion expands immediately. |
| VII — Future and invitation | “This is where we’re starting.” / “Not where we intend to stop.” / “We’re building STEPLOCK. Come build with us.” | Horizontal editorial accent, three planned/exploring directions, an assembled technical illustration and early-access contact setup. | Native reading order; no locked scroll, mandatory sequence or hidden hover content. Contact is intentionally disabled until the founder supplies an address. |

## Timing and interaction ownership

Intervals describe the master story playhead, not a timer or promised reading
duration. Desktop text scenes occupy approximately 100–115 viewport heights in
CSS percent units (roughly one viewport each); Act III includes a separate quiet
scene. Mobile gets its own visual/text stack and longer reading space. The exact
scene state is defined in `storyState.ts`, not duplicated in React state.

Scroll remains reversible and jump links remain usable. Manual explode overrides
separation only; “Drag to explore” suspends authored camera movement while orbit
controls are active. Scroll wheel zoom is disabled to avoid competing gestures.
The four component buttons support keyboard selection in either rendering mode.
The scene's persistent demo link bypasses the entire story.

Pause disables the authored motion and Lenis smoothing. Reduced motion uses the
native/SVG path with discrete chapter configurations and no SplitText reveals.
Graphics failure switches to SVG; the story and demo links remain available. A
measured slow-render fallback also chooses SVG. No 3D payload is required by the
public inspection demo.

The exact explanatory paragraphs and notices live in `CinematicStory.tsx` and
`LandingPage.tsx`. All factual product states in `/demo` continue to come from the
backend; the storyboard has no authority to approve an assembly.
