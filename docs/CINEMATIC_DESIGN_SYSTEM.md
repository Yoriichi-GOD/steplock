# Industrial Requiem design system

This evolves the REQUIEM mechanical identity into a factory-origin narrative.
The compact existing crest remains; fantasy landscape art is not used as factory
evidence. Architecture, negative space, exposed mechanical parts and technical
annotations carry the visual story. No generated product screenshot is used.

## Typography and materials

- Space Grotesk 500: geometric display headings and technical brand wordmark.
- Instrument Serif 400 italic: selective emotional contrast, not whole paragraphs.
- Geist 400/500: navigation, body copy, buttons and the public inspection interface.
- IBM Plex Mono 400: timestamps, chapter indices, source labels and metadata.

The four Fontsource packages are pinned to 5.3.0; Latin-only weights above are
bundled locally with `font-display: swap`. OFL notices are distributed under
`frontend/public/assets/licenses/`. No font CDN is contacted. The private workbench
keeps its existing style files and typography declarations.

Graphite `#080e14`, warm paper `#e7e2d7`, brushed gold `#d8bc84`, titanium and
restrained cool-blue annotations. Actual red/green result states belong to the
inspection workflow. Amber cover emphasis is explicitly illustrative. Brushed
metal uses physically based roughness/metalness, gold/cool rectangular reflection
sources and a moving directional key light. ACES tone mapping, bounded DPR,
512-pixel shadow maps and one environment capture control rendering cost.

Desktop: wide stage, asymmetrical text and procedural factory depth. Mobile: a
dedicated compact SVG stage above readable copy, native scroll and real touch
targets. No essential fact requires hover or completion of the story. Actual
source evidence images receive no color filter, blur or retouching.

## Dependencies and deliberate exclusions

Existing React 19, Three 0.186.1, Fiber 9.8.2, Drei 10.7.9 and GSAP 3.15.0 are
retained. Added `@gsap/react` 2.1.2 (React >=17 / GSAP ^3.12.5) and Lenis 1.3.27
(MIT). GSAP's public package includes ScrollTrigger, SplitText, Flip, MotionPath
and CustomEase under its standard license, not MIT. This presentation website is
within the documented no-charge website use; it is not an animation authoring tool.
[GSAP license](https://gsap.com/community/standard-license/),
[React lifecycle guidance](https://gsap.com/resources/React/),
[Lenis integration](https://github.com/darkroomengineering/lenis#gsap-scrolltrigger).

Motion 14.9.0 is React-19-compatible but would duplicate existing DOM transition
ownership here. Theatre/R3F 0.7.2 declares Fiber ^8.13.6, conflicting with this
project's Fiber 9; it is excluded. Theatre Studio's AGPL license is also distinct
from its Apache-licensed core. Postprocessing 3.2.2 / engine 6.39.5 fit the declared
peers, but bloom/DOF would add rendering passes without a demonstrated need. The
metal reflections and readable evidence work without them. No full-screen GLSL
effect was added to imitate gradients. These are evaluated exclusions, not claims
of integrations.

Leva, r3f-perf and Spector authoring tools are not shipped. Render-call/geometry
diagnostics and browser animation-frame measurements are sufficient for this
iteration; detailed GPU capture remains a future profiling option. A heavy lazy
Three/Drei chunk remains and is reported rather than hidden by changing warnings.
No dev authoring panel or private credential is exposed in the public bundle.

## Interaction vocabulary

Masked line reveals with accessible original text; opposing-direction statements;
scrubbed perspective and assembly movement; a precisely still isolation moment;
technical line drawing; DOM Flip for an evidence document; a restrained horizontal
editorial phrase; ordinary immediate navigation into the genuine demo. No constant
glitch, spinning type, forced preloader, scroll-jacking or fabricated dashboard.
