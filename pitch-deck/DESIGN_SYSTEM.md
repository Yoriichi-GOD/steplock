# Industrial Requiem / investor slide system

Canvas: 13.333333 × 7.5 inches, 16:9. Previews: native PowerPoint 1920 × 1080.
Safe left/right margin: 0.65–0.8 inches. Header metadata: y0.36. Main headline:
y0.98. Primary content generally y2.5–6.65. Footnote divider: y6.96.

| Token | Value | Role |
|---|---|---|
| Background | #05070B | Main canvas |
| Night | #090D14 | Quiet inset surfaces |
| Panel | #101722 | Limited diagram/table regions |
| Blue | #58A6FF | Main lines, structures and labels |
| Ice blue | #76C7FF | Highlights and expressive emphasis |
| Primary text | #F2F0E9 | Headlines and important data |
| Body text | #B7BEC8 | Supporting content |
| Metadata | #788594 | Source notes and secondary labels |
| Brushed gold | #B69A66 | Restrained legacy artwork/material accent |
| Green | #70B49A | Supported PASS observations |
| Amber | #D9A65A | Wrong step and limitations |

## Typography

Georgia 35–49pt for narrative headlines; 59–62pt only for large metrics.
Instrument Serif 400 italic for selected cover/closing emphasis. Geist 18–25pt
for normal supporting text; Geist Medium for useful diagram headers. IBM Plex
Mono 10–15pt for chapter/source/data metadata. Space Grotesk 500 for the compact
solution workflow. Internal static desktop font name from the existing subset is
`Space Grotesk Light Medium`; glyphs come from that 500-weight source.
Tables use 14–16pt. Footnotes are 10–12pt and never contain a hidden positive claim.

Fonts stay editable in PPTX; they are not embedded or shipped as standalone files.
For exact appearance use the PDF. When editing on a new device, install the same
families from their official Fontsource projects, or use PowerPoint Replace Fonts:
Geist → Aptos/Arial, Instrument Serif → Georgia Italic, IBM Plex Mono → Consolas,
Space Grotesk → Arial. Georgia remains the principal display fallback. Check line
wrapping after replacement; no substitute can guarantee identical metrics.

## Compositions

Opening/closing: actual celestial artwork, original ornate image logo and native
headline typography. Central slides: clean editorial framing, native assembly
components, timeline, evidence pipeline, actual screenshot, chart, founder profile,
milestones, ambition horizon and financial table. No full-slide rasterization.

Blue dominates new graphical content. The gold and floral identity is preserved
inside original artwork, not recreated using guessed fonts. Product evidence is
unfiltered. The sole stock photograph is labeled illustrative; no worker is shown
as responsible for an error. No synthetic industrial photo is used as proof.

Connectors use valid nonnegative extents; arrowheads follow source-to-target flow.
Two-step examples are labeled conceptual. Diagrams never use animation to imply
successful recognition. Native Fade transitions are supplementary; the PDF tells
the whole story. All slides retain their complete information in static form.

Reusable authoring helpers are in `src/build_deck.cjs`: text, line/arrow, plate,
marker illustration, frame, table, section header/footer and source/speaker notes.
