# Motion ownership

| Movement | Owner | Cleanup / scope |
|---|---|---|
| Story playhead, stage pin, camera/part/light progression | GSAP timeline + ScrollTrigger | Scoped `useGSAP`, matchMedia revert on mode change/unmount |
| Desktop smooth wheel scroll | Lenis through the GSAP ticker | `autoRaf:false`; listener/ticker removed; instance destroyed |
| Responsive masked heading lines | SplitText | `autoSplit:true`, line masks, ARIA auto, returned animation from `onSplit`; revert on cleanup |
| Opposing statements, perspective entry, editorial travel | GSAP ScrollTrigger | Same scoped lifecycle; no Motion animation competing for properties |
| Dependency/station path | Native SVG dash length + GSAP MotionPath | Recreated with responsive matchMedia; no competing 3D transform owner |
| Evidence document expansion | GSAP Flip | Capture DOM state, React commit with `flushSync`, then `Flip.from`; context-safe event handler |
| Direct component selection / mode / contact | React state | No authority over inspection verdicts |
| Actual source frame / live status | Existing session API + React | No decorative animation sets or preserves PASS |

## Scroll architecture

Lenis exists only for a fine-pointer desktop >=1000 px with motion enabled. Native
scroll is used on mobile, reduced motion and paused mode. Anchor support is enabled;
forms and nested interactive panels opt out. `lenis.on('scroll', ScrollTrigger.update)`
connects scroll state; one `gsap.ticker` callback passes seconds ×1000 to `lenis.raf`.
There is no ScrollSmoother, second RAF controller or smooth-scroll React wrapper.
[Official Lenis pattern](https://github.com/darkroomengineering/lenis#gsap-scrolltrigger).

ScrollTrigger drives a normalized scalar. The pure bounded interpolator in
`storyState.ts` defines the visual pose. The Three scene and SVG read the same
pose; the DOM does not maintain a second camera timeline. An explicit 0.65–0.73
pose plateau provides stillness. Manual explode replaces separation only; manual
orbit temporarily owns the camera. The authored timeline retains all other values.

## Typography and accessibility

Only principal headings are split into lines, not every word or character.
Original text remains accessible through SplitText ARIA handling, and heading
semantics/reading order remain intact. Re-splitting responds to font load and width.
The initial HTML/CSS displays useful copy and SVG while WebGL is loading; no
full-screen preloader or mandatory story sequence blocks the prototype link.
[SplitText lifecycle](https://gsap.com/docs/v3/Plugins/SplitText/).

CustomEase `requiem` is defined once. It coordinates introductions/Flip without
continual bounces or decorative glitch. A short blur is restricted to the opening
eyebrow; evidence pixels are never blurred. On reduced motion all text remains
plain, the timeline uses discrete chapter poses, SVG is default, and Flip expands
instantly. The pause control also removes Lenis and animated reveals.

ScrollTrigger pinning is desktop-only; the native sticky mobile stage occupies its
own visual band so text can be read below it. Ordinary hyperlinks navigate into
the real `/demo` immediately. The main story's persistent prototype link allows
visitors to leave at any moment. No client animation manufactures API results.
