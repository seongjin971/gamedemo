# Tree V10 structural crown replacement

Status: READY FOR NATIVE UNITY CANDIDATE REVIEW. This asset-only result does not
establish a scene score, user adoption, movement quality, or FPS.

Read `Migration/Evidence/AtmosphereV2/verdict-unity-5.md` and directly inspected
the concept plus candidate-30 full, orbit, and zoom images. Also read the V8/V9
construction scripts and directly inspected V9's neutral geometry preview.

## What changed visibly

The old crown and all its fine needles were removed. Eight authored major
systems now use continuous smooth centerlines with tapering ends, 32 unequal
curved offshoots, and 16 smaller fork divisions. The three prominent upper
elbows are replaced by broad curved transitions. This changes the silhouette
and branching hierarchy, rather than adding more texture to the old branches.

The lower-trunk form was sampled from V9 (2,096 source vertices), joined with a
continuous overlapping bridge, and unioned with the new crown. The major wood
is one connected component (19,457 vertices after the core budget pass).
It retains the lower-trunk placement and lean, but is not vertex-identical after
union, smoothing, and the bridging work.

The old uniform radial root fan is removed. Four asymmetrical buttresses have
authoring radii of 0.22-0.24 near their trunk attachments, versus 0.082 for four
small feeder roots. Their flattened outer widths are roughly 2.5-3.5 times the
feeder widths. Roots terminate at unequal distances/heights; stone-gap contact
must still be checked in the actual Unity scene. 446 unequal raised bark patches
interrupt the larger surfaces. Packed original bark images are reused, with
longitudinal UVs from the newly authored wood reprojected after the union.

## Direct visual assessment

Opened the final `tree-v10-preview.png` and `tree-v10-geometry.png` and their
matched `tree-v9-same-light.png` and `tree-v9-geometry.png` in
`.dream-loop/unity-atmosphere-v2/tree-v10/`. All use the same 1152x1152 camera,
lights, exposure and background. Neutral images isolate geometry from bark.

The new crown is immediately different: the many disconnected-looking straight
needles and sharp zigzag upper limbs have become clean curved split branches.
The lower trunk is visibly continuous, and three of the four larger buttresses
are distinct from this camera. Raised bark is visible in neutral geometry and
the longitudinal texture now follows the new limbs without the initial severe
crosswise distortion.

Limits remain: the crown is cleaner and less densely ramified/gnarled than the
concept. Several long middle limb surfaces still read relatively smooth between
raised patches. The roots are more massive and less tangled than the concept;
ground burial and contact shadows need native scene inspection. These are
material/silhouette limitations, not hidden by the triangle QA. This is a
substantial structural response to the repeated tree blocker, not a claim that
the entire Tier 3 gate has passed.

The first local preview was rejected because the cropped lower trunk did not
properly connect and the buttresses were too broad. Those defects were corrected
before this delivery. Initial rejected preview/report evidence is retained under
`rejected-initial/` and must not be treated as the final result.

## Technical result

- Final export: 83,778 triangles, 48,711 vertices, below 100k triangles.
- All position, normal and UV values finite; indices in range; normal lengths
  0.999999877 to 1.000000145; zero exported degenerate triangles; zero triangle
  winding disagreements with average normals. Two zero-area source triangles
  were skipped, and six tiny tip faces use their geometric face normal.
- Main wood is one connected component. Small tips and bark relief retain
  overlapping surfaces as in prior assets; this is not a single watertight mesh.
- Unity coordinates are `(-x,z,-y)`, with triangle corners reversed `[0,2,1]`
  exactly once. Original local transform is identity and retained exactly.
- Blender crown maximum Z is 6.476829, versus V9 6.510002. Lateral width is
  6.019447, versus V9 6.290008. Origin is unchanged.
- Source V9 blend SHA256 remains
  `2c42381b49062e50b98c4dda6c5b1670db57be54fa8dddde12d21444a6ce0aeb`.
- Final JSON SHA256:
  `67bc99ed718d767962708ee9c5e8e0dfa8a8eb60fa168bcc984d4696984b7d58`.

`build_tree_v10.py` reproduces modeling, packed blend, JSON export and four
comparison renders. `validate_export.py` independently checks the JSON and
source preservation and writes `export-qa.json`. Blender printed V10 COMPLETE,
saved all four final images and exited. PowerShell reported a Blender 6.0
material-API deprecation warning, and Blender noted three unfreed shutdown
blocks totaling 0.014305 MB; there was no Python traceback or missing output.

No previous source, Unity file, browser file, scene, material configuration, or
other agent's file was changed. Work is confined to the assigned V10 source and
V10 `.dream-loop` evidence folders.
