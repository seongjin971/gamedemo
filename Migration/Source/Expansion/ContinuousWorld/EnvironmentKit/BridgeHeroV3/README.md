# Bridge V2 visibility diagnosis — no replacement mesh

This folder contains diagnostic renders/scripts only. No V3 mesh or Art exports were produced. V2 remains unchanged. Dense testing disproved the proposed explanation that failed Boolean spandrels had filled the opening.

## Geometry evidence

`diagnose_v2.py` imported the original V2 FBX. At every requested source height (-.35,-.6,-1,-1.5,-2), all81 horizontal rays placed inside98% of the analytic ellipse span pass completely through the6.5m-wide bridge. The same passes at -2.6. All eight probes outside the ellipse at each height hit masonry. `v2-true-side-diagnostic.png` directly shows the full open arch against a contrasting background. `v2-diagnosis.json` preserves the measurements.

Only the extreme crown boundary within1–3cm of -.22 differs slightly from a perfect mathematical ellipse because of the26-segment polygonal voussoirs. At -.23,59/81 interior probes pass; at -.25,77/81 pass. This small boundary approximation does not explain a large solid side wall, and replacing the entire bridge would not address the main visual issue.

## Camera and water comparison

`render_camera_comparison.py` uses the original V2 geometry, changing only vertices below local-up0 by×1.5 as in the parent. Water is world-.95. Resolution1536×1024, Unity orthographicSize8.2 corresponds to16.4m vertical/24.6m horizontal extent. The target follows the d45 player location,3.5m toward the near end from bridge center, plus about1.09m above the deck. The Blender source-camera X sign is mirrored to match the handedness of the imported Unity FBX view; the final renders match C04's bridge orientation.

| File | Deck | Angle / Elevation radians | Water body |
|---|---:|---|---|
| A-current-angle-raised-shadow.png | 2.8 | .46 / .72 | receives light/shadows |
| B-wider-lower-angle-raised-shadow.png | 2.8 | .60 / .62 | receives light/shadows |
| C-current-angle-original-deck-shadow.png | .8 | .46 / .72 | receives light/shadows |
| D-wider-lower-angle-original-deck-shadow.png | .8 | .60 / .62 | receives light/shadows |
| E-current-angle-raised-water-unlit-control.png | 2.8 | .46 / .72 | flat emission control, no body-shadow response |

The lighting/water are controlled Blender inspection materials, not a reproduction of Unity's complete river shader, reflections or landscape. In particular E isolates loss of body-shadow response; it is not a claim of exact Unity shader equivalence. These are asset/camera diagnostics, not a fresh independent whole-scene quality score.

The raised-deck arch crown is world2.47, leaving3.42m maximum opening above water. Original deck.8 leaves only1.42m. Numerically integrating the ellipse and projecting its front-face aperture gives2.05% of frame area at raised deck/.46/.72 versus2.82% at raised deck/.60/.62, a38% increase. Original deck drops those to.60%/.83%. See `analytic-aperture-projection.json`. These geometric projection estimates exclude scene occluders and shading; they help choose a useful camera comparison, not assert perceived quality.

Recommendation: retain the raised deck if route compatibility remains acceptable, compare Angle.60/Elevation.62 in the real scene, and make the water body receive bridge shadows. Preserve V2 geometry while testing those visibility changes.
