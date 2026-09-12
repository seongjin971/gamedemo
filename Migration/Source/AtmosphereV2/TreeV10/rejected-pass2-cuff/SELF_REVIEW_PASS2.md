# Tree V10 pass 2: native silhouette correction

Status: READY FOR NATIVE CANDIDATE 33 REVIEW. The final JSON is stable.

Directly opened native `round-32-tree-water/full.png` and `zoom.png` beside the
concept. Pass 1's crown was too thick, smooth and sparsely divided at actual
scene scale, and its four roots read as giant pointed toes. Pass 1 is preserved
under `Migration/Source/AtmosphereV2/TreeV10/pass1/` and the matching evidence
`tree-v10/pass1/`; those files were not overwritten.

## Structural correction

- Narrowed most upper and lateral limb diameters approximately 20-35%, with
  stronger taper earlier along their lengths. Re-authored unequal directional
  changes through the main leader and seven lateral systems, keeping smooth
  junctions across the bends rather than the original straight needle joints.
- Added ramification at several unequal distances along each major limb:
  48 curved tapering offshoots and 80 smaller curved fork divisions, compared
  with pass 1's 32 and 16. These are connected-looking curved wood forms that
  overlap their parents, with longitudinal bark UVs. No old needle meshes return.
- Four root collars now descend sooner. Their outer cross sections flatten
  vertically to 22% of the original round profile and run at or below the origin
  ground plane. Their directions and endpoints are unequal. Base radii of
  0.18-0.20 versus feeder radius 0.065 maintain roughly threefold width hierarchy.
- Rebuilt the descending central rootstock to avoid the first revision's
  cuff-like exposed bottom cap. Preserved 1,075 V9 lower-trunk source vertices
  between heights 0.80 and 1.66 before union, and recessed the upper splice
  inside the overlapping crown. This preserves form and placement rather than
  exact vertex positions. Main wood is one connected component.
- 364 raised unequal bark patches remain on the major wood. The existing
  packed bark images and the authored longitudinal UV transfer are reused.

## Actual preview review

Directly opened the final material preview and neutral geometry preview and the
identically lit/framed pass 1 pair. Files are in
`.dream-loop/unity-atmosphere-v2/tree-v10/`:

- `tree-v10-preview.png` and `tree-v10-geometry.png`: final pass 2.
- `tree-v10-pass1-same-light.png` and `tree-v10-pass1-geometry.png`: preserved
  pass 1 rendered in exactly the same rig, 1152x1152.

The difference is visible across the crown: thinner upper branches, a less
uniform leader, more smaller split branches between major limbs, and much
flatter root tails. The former large toes and unbroken broad upper curves are
reduced. The lower rootstock is continuous. This is a meaningful response to
the observed native screenshot, not a conclusion derived from mesh counts.

Remaining limits: the crown is still more organized and some broad grain
stretches smoother than the concept's deeply broken, irregular bark. The finest
branches can be subpixel at native full-frame distance. Ground burial and root
contact must be verified in candidate 33 because the isolated Blender rig has
no Unity paving. The asset preview does not establish a scene tier, FPS,
movement acceptance, or final adoption.

## Verified export

- 90,816 triangles / 52,633 exported vertices; below 100k triangles.
- Finite arrays, index bounds valid, unit normals within 1.3e-7 of length one.
- Zero degenerate export triangles and zero winding/normal disagreements.
- No zero-area triangles needed discarding in this revision. Nine tiny cap
  triangles use their geometric face normal to avoid opposing averaged normals.
- Major core has one connected component of 17,900 vertices. Fine branches
  and bark plates are overlapping surfaces, not one fully watertight mesh.
- Original identity transform retained. Export maps `(-x,z,-y)` and reverses
  triangle corners `[0,2,1]` once, as prior Unity assets do.
- Blender bounds: X -3.360588 to 2.989870; Y -1.133100 to 1.089852;
  Z -0.165432 to 6.394671. Crown width is 6.350457, versus V9 6.290008;
  maximum height is 6.394671, versus V9 6.510002.
- Final JSON SHA256:
  `74be4a67f2170476cd2daa3f7dde8c969b5e22e32ff5910d6215676cdacdbe7a`.
- Pass 1 blend SHA256 remains
  `4aeb4d0dc3e0cf13beaf2a33fd0a90dcc5736761b1163238b977d0fcd28e6674`.
- V9 blend SHA256 remains
  `2c42381b49062e50b98c4dda6c5b1670db57be54fa8dddde12d21444a6ce0aeb`.

Build and independent validator remain `build_tree_v10.py` and
`validate_export.py`. Final checks are in `export-qa.json` and
`tree-v10-report.json`. No Unity, browser, previous version, or other agent's
files were edited. All writes remain inside the two assigned TreeV10 folders.
