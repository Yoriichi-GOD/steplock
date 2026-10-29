# Assembly explorer

The Procedure Studio includes an optional procedural 3D illustration of the
BASE, SPACER, COVER and FASTENER recipe groups. Use **Explode assembly**, drag
to orbit, select a mesh or component button, and inspect its recipe step,
required zone, tag identity and prerequisites. The separation slider supports
partial disassembly. **Play assembly / Show correct order** illustrates the
validated recipe DAG in dependency order. **Hide explorer** brings the original
inspection controls back into view. Presentation mode has an explicit exit.

## Evidence boundary

The illustration is not CAD, a reconstruction from camera pixels, a measured
physical design, or evidence of fastening/torque. The physical-looking stack
explains the four recipe roles; the actual detector checks tagged placements in
the board's specified zones. Only the actual frame/engine path can confirm steps
or corrections. No viewer control writes to the session engine.

- Green: the session reports CONFIRMED and the source is connected, usable,
  calibrated and has no unresolved uncertainty about order.
- Red: an unresolved wrong-part, wrong-zone, wrong-order, missing-at-checkpoint
  or unknown-part finding maps to the illustrated part. Unexpected identities
  map through their required zone; the original finding retains its observed ID.
- Amber: source loss, unusable/uncalibrated capture, uncertain order, or a finding
  that cannot be mapped safely. Historical confirmations do not remain green.
- Neutral: no session or placement not yet proven.

Corrected findings leave the immutable history intact. The inspector's evidence
button opens the existing Evidence Explorer at the actual engine event. Human
acknowledgement and demonstration animations never remove a red finding.
Synthetic sessions are visibly labeled inside the explorer, including in
presentation mode.

## Offline and fallback behavior

All geometry and lighting are generated locally with Three.js, React Three
Fiber, Drei and GSAP. No remote model, font or environment texture is needed.
The 3D scene is a separate lazy-loaded bundle (approximately 275.5 kB compressed
in the verified build). The normal production build emits a size advisory for
the 3D bundle; it succeeds.

Use **Use 2D diagram** for a schematic. A lost/unsupported graphics context also
falls back to the diagram while inspection and evidence controls remain usable.
Custom recipes without the four recognized geometry roles use their own step
diagram instead of an invented 3D model. Reduced-motion preferences disable the
animated sequence and auto-rotation; manual separation changes immediately.

## Verification

Run `npm test` and `npm run build` from `frontend`. Ten focused tests cover
unresolved/corrected findings, acknowledgements, unexpected identities, stale
sources, capture quality, calibration, uncertain order and dependency ordering.

Browser checks are recorded in [UI_COORDINATION.md](UI_COORDINATION.md).
Screenshots in `screenshots/assembly-*.jpg` are authentic local browser captures
of synthetic software-test sessions. They do not establish physical camera
validation or physical assembly accuracy.

Implementation references: [React Three Fiber](https://r3f.docs.pmnd.rs/getting-started/introduction),
[Drei controls](https://drei.docs.pmnd.rs/controls/introduction),
[GSAP](https://gsap.com/docs/v3/GSAP/gsap.to()/).
The user-provided industrial viewer was inspected for interaction direction;
its source/assets were not copied into this implementation.
