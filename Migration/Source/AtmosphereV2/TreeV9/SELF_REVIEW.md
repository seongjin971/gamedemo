# Tree V9 structural candidate self-review

Basis: read `verdict-unity-4.md` and directly opened the concept and actual
`round-23-fixed/full.png`. The previous whole-frame lighting pass is preserved
by this asset-only task; no Unity, material configuration, Git, or protected
source files were edited.

## What is structurally different

- Four individually directed, flattened, asymmetrical buttress roots climb the
  stump and extend into the existing root fan. These are unioned with the major
  wood; the many existing thin distal roots are retained. The silhouette now
  has several substantial flares rather than only similarly sized radial tubes.
- Three upper bend regions change over approximately a local branch diameter,
  followed by continuous remeshing/fairing. The final 28% of retained thicker
  terminal meshes receives additional smooth taper. Eight *fine* offshoots are
  selected separately from V8's thick terminal replacements, and rebuilt as
  cubic curved limbs that split once, with continuously diminishing radii.
- 639 individually unequal, raised bark patches are projected onto the actual
  major wood surface, including the long branches and new buttresses. Their
  asymmetric crests rise approximately 1.4-3 cm on the larger wood and scale
  down on small limbs. Broken ends, skew, variable lengths and widths, and
  occasional missing corners make short transverse separations between the
  longitudinal patches. These are actual geometry, not extra normal-map noise.
- Existing bark images are reused. Native bark UVs are reprojected on the
  continuous main mesh, with longitudinal UVs on new bark patches and twigs.

## Actual inspection

Directly opened the final 1280x1280 `tree-v9-preview.png` and the identically
framed/illuminated `tree-v8-same-light.png`. The larger uneven root flares and
additional curved forks are visible. Long limb highlights are interrupted by
the new raised surface instead of remaining entirely smooth tube highlights.

Also rendered and directly opened `tree-v8-geometry.png` and
`tree-v9-geometry.png` with the same neutral material and camera. This isolates
geometry from bark texture: the interrupted relief across the long upper-left,
middle-right and lower diagonal limbs is visible, as are the four buttress
volumes. Thus the difference is not being inferred only from vertex counts or
small numeric displacement.

Remaining limits are visible: some retained fine twigs still contain straight
segments; several tiny original splinter forms remain; the center of some
major surfaces is relatively smooth between patches. The tree retains its
existing stylized branching composition and does not yet establish the full
concept's bark and silhouette fidelity. Native frame-scale readability under
VESPER's dark cool lighting must be compared and judged independently. These
asset previews are not a claim of Tier 3 completion or final acceptance.

## Technical result and preservation

- **74,671 triangles / 45,536 exported vertices**. V8 had 51,654 triangles:
  +23,017 (+44.56%). This is below the requested 80k triangle ceiling.
- JSON arrays are finite, indices are in range, normals are unit length, and
  exact position/normal/UV tuple sharing retains UV seam splits. See
  `export-qa.json`.
- Blender `(x,y,z)` becomes Unity `(-x,z,-y)`; triangle corners are reversed
  `[0,2,1]`. The source texture basis and object scale are preserved.
- Overall lateral/depth bounds and crown height remain effectively identical.
  The lowest Unity Y moves only from -0.167212 to -0.164164 (about 3 mm).
  Exact source/target bounds are recorded in `export-qa.json`.
- Tracked V8 source SHA256 is unchanged:
  `cb81549809888a1e71faebab0aa767cfaa0104ebeba953450cc7df8b69576f3b`.
- All outputs and scripts are confined to this new `tree-v9` folder.

Build: `build_tree_v9.py`. Export: `tree-v9-mesh.json`, `tree-v9.blend`.
Verification: `validate_export.py`, `export-qa.json`, `tree-v9-report.json`.
Neutral comparison: `render_geometry_review.py` and the two geometry PNGs.

The final asset build completed both color captures and exited. Blender noted
three unfreed shutdown blocks totaling 0.023312 MB. The separate neutral-render
command produced a Blender `Material.use_nodes` deprecation warning that
PowerShell reported as a native-command error; both requested images were
nevertheless saved and directly inspected, with no Python traceback. No
rendering or Blender process remains running from this task.
