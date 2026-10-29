# Staged camera recordings

REAL_STAGED_DATA: NOT_PROVIDED at build start. Do not substitute generated frames.

Capture only harmless tabletop components with consent; no faces or audio needed.
Print `demo_kit/printable_board.png` and cut the labeled tags from `markers.png`.
Keep corner markers fixed and all parts visible. Use overhead 640×480 or 960×540.

Record at least 12 independent clips across normal (3), wrong component (2), wrong
zone (2), early cover (2), missing fastener (1), correction (1), occlusion (1).
Start with a clear empty board. Wait 0.5 seconds after each placement. End with an
explicit final checkpoint. Include a second camera setup when possible.

Before scoring, annotate onsets, the next prohibited boundary, expected verdict,
camera group, recipe SHA and consent. Split by complete clip/setup/operator, never
adjacent frames. `python scripts/register_recording.py --help` documents manifest
registration and hash validation. Real recordings remain ignored by Git; publish
only with separate consent to public redistribution. Upload in the Studio to test.
