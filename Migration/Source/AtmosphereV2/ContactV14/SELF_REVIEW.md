# ContactV14 source self-review

## Direct visual evidence

All five final 1536 x 1024 Blender images were opened directly after the final PavingV14 reprojection: `overview-before.png`, `overview-after.png`, `clusters-before.png`, `clusters-after.png`, and `contacts-after.png`. Matching before/after views retain the complete unmodified paving and intact TreeV12. The retained first context experiment used a cropped tree with distracting open cut surfaces; those old images are excluded from final visual assessment.

The matched overview and cluster pairs show fewer isolated small cuboids, four unequal fragment groups, and larger flat wedges with open intervals between them. The 49 retained original pieces remain intentionally visible. Group membership is asymmetric, with 7, 5, 6, and 8 new fragments; measured maximum/minimum diameter ratios are 3.153, 3.319, 2.856, and 3.264. This provides actual size hierarchy and spatial grouping, rather than additional uniformly scattered detail.

The final contact view shows small brown/olive deposits beside the visible roots. The fourth contact uses the actual inward parapet surface because its outer root terminal lies beyond the floor. Some deposits are partly hidden by the unchanged large root and wall geometry. They should not be described as four equally readable marks in every view.

## Technical evidence

The final independent export check passed after the final render. Rubble is 508 triangles; deposits are 576. Every exported triangle has positive cross-product dot supplied normals; degeneracies and welded edge errors are zero. Geometry has finite values, unit normals within measured floating-point tolerance, positive signed volume, and closed bodies. The exact removal manifest verifies all fields for 50 original instances and records 49 preserved peers. Source TreeV12 and PavingV14 hashes remain unchanged.

Rubble world bounds are X [5.143568, 8.470000], Y [-0.043330, 0.087812], Z [-6.849108, 1.094612]. Deposit bounds are X [4.360619, 8.678016], Y [-0.082600, 0.224214], Z [1.058614, 6.632276]. Negative underside heights are intentional burial, not unsupported floating bodies. Actual floor sample changes from V13 to V14 are documented in `HEIGHT_REPROJECTION.md`.

Both assets export native Unity world coordinates and require identity transforms. Tree origin, yaw, scale and navigation clearance are unchanged. There are no new textures, generated API assets, grass specks, or Unity file edits in this package.

## Remaining limits

The local grouping improvement is ready for native comparison. Neutral clay renders still make some fragment faces look clean and polygonal. Existing Rock05 grain and native shadowing must be judged in Unity before claiming weathered realism. Brown/olive deposits are authored mineral-grain contact suggestions, not scanned soil or botanical moss. Their native material response, partial occlusion and close-camera integration remain open.

No FPS or gameplay result follows from triangle count. No scene-wide score, Tier 3 pass, Dream Loop completion, or user adoption is assigned by this source review.
