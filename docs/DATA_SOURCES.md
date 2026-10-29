# Sources, acquisition and licensing

Checked 29 October 2026. External dataset descriptions are not STEPLOCK results.
Raw downloaded annotations are ignored under `data/`; no public videos were downloaded.

| Source | Use / observed status | Rights / boundary |
|---|---|---|
| Team-supplied organizer graphic/message | theme transcription and repo/hourly rule | supplied source; detailed public document not independently retrieved |
| OpenCV | actual installed 4.14.0 ArUco API | dependency license retained; OpenCV 5 is not claimed |
| Generated STEPLOCK fixtures | 48 deterministic software clips, eight tracked examples | source code in this repo; visibly synthetic; truth separate |
| Consented staged-real clips | NOT_PROVIDED | capture and public redistribution require human consent |
| Assembly101 mistake annotations | 328 CSVs / 3,964 rows; 195,207-byte archive | CC BY-NC 4.0; local inventory only; no numeric task benchmark |
| HoloAssist | official dataset/license page reviewed; no bulk media | source states CDLAv2; no footage/score bundled |
| IKEA ASM | official repository reviewed; no media/model use | code and dataset media rights must be considered separately |

Assembly101 observed labels: 2,927 correct, 707 mistake, 330 correction. Headerless
seven-column CSVs retain every first annotation. An initial DictReader assumption
was caught; the original local inventory remains, with a new audited inventory
and parser tests. [Published metadata only](ASSEMBLY101_INVENTORY.json).

Attribution: F. Sener et al., *Assembly101* (CVPR 2022); G. Ding et al., *Every
Mistake Counts in Assembly* (2023). No defensible mapping from their toy actions to
our four-tag placement recipe was available. Annotation-only and visual scores are
NOT_RUN. Noncommercial data does not make a commercial deployment cleared.

Primary links:

- [Organizer listing](https://unstop.com/hackathons/cypher-digiweek-jc-bose-university-of-science-and-technology-ymca-faridabad-1771873) — extractor returned no readable text.
- [Organizer-linked detail](https://drive.google.com/file/d/1pS4oJgDjLmRYuLvVLlawaNc_V9LGopEB/view) — not independently retrieved.
- [OpenCV marker documentation](https://docs.opencv.org/4.x/d5/dae/tutorial_aruco_detection.html).
- [Assembly101 project](https://assembly-101.github.io/), [annotations](https://github.com/assembly-101/assembly101-mistake-detection), [license](https://github.com/assembly-101/assembly101-mistake-detection/blob/main/LICENSE).
- [Every Mistake Counts](https://arxiv.org/abs/2307.16453).
- [HoloAssist official project](https://holoassist.github.io/).
- [IKEA ASM official repository](https://github.com/IkeaASM/IKEA_ASM_Dataset).

Runtime uses local system fonts and original procedural graphics. Third-party
dependency licenses remain in their installed distributions. No remote texture,
font, model or cloud inference request is needed for a launched offline demo.
