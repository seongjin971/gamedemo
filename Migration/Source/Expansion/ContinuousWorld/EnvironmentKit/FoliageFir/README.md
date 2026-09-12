# Carded alpine fir

`CW_CardedAlpineFir.fbx` and `CW_CardedAlpineFir_LOD1.fbx` are 9 m tall conifers with a maximum 5 m crown width. A real tapered woody skeleton carries radially oriented, curved, crossed branch cards. Each card selects one of the four supplied alpha sprays; there is no whole-tree billboard. The source atlas is unchanged and its SHA256 is recorded in the manifests.

LOD0 is 8,732 triangles; LOD1 is 6,276. Both share branch positions and normalization so switching LOD does not change the tree structure. Foliage has canopy-volume custom normals to reduce obvious flat-card lighting. Preserve imported normals when practical.

**Preserve the FBX node conversion rotation.** Exported nodes contain X = -90 degrees so Blender Z-up becomes Unity Y-up. Put world position, yaw and desired scale on a wrapper around the imported prefab; do not overwrite imported model-root rotation.

- `CW_FirNeedles`: full `Art/Textures/FirBranches.png`, no material ST/quadrant remap. UVs already select the four quadrants. Opaque alpha clipping at cutoff 0.35 is the preview setting; use Cull Off and a matching alpha-clipped shadow caster.
- `CW_FirBark`: full `Art/Textures/WorldSurfaceAtlas.png`, no material ST remap. UVs already select bottom-left bark, ranging 0.025..0.475 on both axes.

The final Blender preview is `fir-preview.png`. Earlier previews are retained to document opening the canopy and fixing the LOD correspondence. `uv-axis-audit.json` records raw FBX transforms, triangle integrity and per-material UV bounds for the original kit, chapel and fir. This preview is not Unity lighting/performance acceptance. Use LOD0 selectively for foreground trees and measure alpha/shadow cost in the actual scene; triangle count alone does not establish GPU cost.
