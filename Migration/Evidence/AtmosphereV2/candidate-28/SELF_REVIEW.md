# Candidate28 self-review and safe stop

Status: `PAUSED_BY_USER / TECHNICALLY_VALID / NOT_JUDGE_READY / VISUAL_TARGET_NOT_MET`.

Directly inspected at native capture resolution against `Migration/Reference/concept.png`, the browser baseline and candidates23,26,27. `full.png`, `orbit.png`, `zoom.png` are1536x1024 and `slice.png` is1037x739.

Changes represented by this capture:

- KnightV5 replaces the cape mesh through the existing hierarchy and material-preserving importer. Its broad silhouette, softer unequal folds and shallow uneven hem remain visible in Unity.
- The separate standing-water layer uses a tight three-tap reflection instead of the former wide vertical blur. Cool reflections are restrained and warm reflection shapes remain more localized.
- Photographic-stone albedo is no longer multiplied into clipped gray. Dry measured normals are stronger, roughness has a nonzero floor, and underlying floor wet smoothness is reduced where separate standing water is used.
- The DepthNormals path initializes `normalTS` before the shared stone-normal function.

What landed: the large white cloud-like water smears of candidates26/27 are substantially reduced; warm reflection silhouettes are clearer; the V5 cape's softened fold/hem treatment survives the scene scale. `capture.json` records shader errors0, runtime errors0, missing scripts0 and120 reflection updates on Intel Arc130V.

What remains blocking: several wet areas still read as broad dark blotches instead of shallow irregular water; Rock01 surface relief remains too subtle at the full-frame distance; regular portal/stair courses and remaining tree silhouette issues still block Tier3. This candidate was not submitted for independent judging and receives no new score.

Not performed before the requested stop: Windows player build, noninstrumented FPS, direct input, continuous movement/orbit/zoom review, animation review, independent judge, or user acceptance. The last independent Unity score remains candidate23 at5.4/10 Tier2.
