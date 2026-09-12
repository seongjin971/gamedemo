# Knight V6: shoulder normal repair and constrained helmet shell

Status: READY FOR NATIVE UNITY REVIEW. This is a bounded asset correction, not
a whole-character or scene acceptance claim.

Read V5 BUILDER, SELF_REVIEW, INTEGRATION_STATUS, export validation and source
scripts. Directly inspected native candidate 35 full/zoom and candidate 36 zoom,
the concept, and V5 studio preview. Read the actual working Unity NativeMesh
function and import mapping. No Unity files were edited.

## Changes and preservation

The two shoulder steel meshes each contained 60 triangles whose geometric face
direction disagreed with the averaged exported normal. The source is the tiny
64-sided center cap left by the radial shell construction, including the
solidified underside cap. V6 collapses each tiny cap ring to its centroid,
recalculates the closed shell normals, and retains creases above 55 degrees.
This repairs topology rather than flipping an entire mesh's normals or hiding
failures in the importer. Each steel record drops from 3,324 to 3,072 triangles.
All six shoulder bound planes remain exactly unchanged.

The existing Angular_closed_bascinet shell was an 80-triangle flat-shaded
icosphere. Two subdivision levels with smooth normals produce 1,920 triangles;
the result is constrained to all six original bound planes, without changing
its position, scale or parent. The visor, nasal ridge, eye slit, hinges, gorget
and all other authored plate/ridge meshes remain exact. No blanket smoothing
was applied to those plates. The separate helmet JSON maps the existing object.

The seven-record pack retains names/order and copies FIVE V5 records exactly:
the cape, both shoulder rims and both arm-trim groups. Their positions, normals,
UVs, indices, counts and metadata are unchanged. The candidate blend also retains
the original shoulder rim loop normals so preview shading agrees with the copied
rim records. All original Blender object names, parents, transforms, material
slots and visibility states are exact; every other Blender mesh is exact.

## Actual final preview inspection

Directly opened all four final matched renders after the final build:
`preview-before.png`, `preview-after.png`, `armor-before.png`, and
`armor-after.png`. Whole-body images are 800x900; close armor images are 900x900.
Each pair uses the identical camera, lights, original materials, 32 Cycles samples
and AgX exposure. No preview light/camera is saved in the candidate blend.

The large triangular helmet highlight patches are gone. The helmet silhouette
is rounded within the original envelope, while the separate hard visor/ridge
details remain. There is no new seam, exposed cap, helmet inflation or obvious
intersection in these inspected views. The cape shape and attachment remain
visually unchanged. Shoulder width is unchanged, and the pole repair does not
visibly disturb the broad shallow plate surfaces.

Actual limits: inherited metal materials still produce broad bright glossy
highlights in this studio rig. This geometry/normal task does not solve native
metal roughness; root owns that Unity change. Arm and torso planes remain
deliberately faceted as inherited, and the helmet shell is still simple rather
than richly tooled or damaged metal. At native full-frame character size,
shoulder pole repair may be visually subtle, while the helmet's triangular
highlight removal should be the clearer change. Native screenshot review is
still required; no runtime, FPS, animation or final adoption result is claimed.

## Independent data QA

`validate_knight_v6.py` independently reproduces the live Unity formula:
`Dot(Cross(pb-pa, pc-pa), na+nb+nc)`, with its -1e-10 outlier threshold. It also
requires every final normalized face/average-normal dot to be strictly positive.

- Shoulder outliers: 60 + 60 before, zero + zero after.
- Minimum final shoulder alignment: 0.998836 left, 0.998822 right.
- Helmet minimum alignment: 0.998673; zero negative-dot triangles.
- All eight delivered records: finite arrays, valid indices, nonzero triangle
  areas, unit normals within 1.3e-7, and strictly positive alignment.
- Main seven-part pack: 15,720 triangles; helmet supplement: 1,920 triangles.
- Cape and four other records pass exact equality against V5. Source V5 blend
  and JSON SHA256 are unchanged. Full hashes and bounds are in `export-qa.json`.

Stable delivery hashes:

- Seven-part JSON:
  `0d2246118d6c9534a949cbfc13774b88dd1f72aadb14b3da080bc1c887f4ec25`
- Helmet supplemental JSON:
  `e57503a85be1d6d67870e9dee425d4ff2a98e712cf89be5cbdc42a9982c9c2fe`

Final Blender build and all four renders exited successfully, with no Python
traceback. All files are confined to KnightV6 source/evidence. TreeV10 remained
frozen throughout this task.
