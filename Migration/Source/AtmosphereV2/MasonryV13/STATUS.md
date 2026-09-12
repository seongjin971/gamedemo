# Source ready for native comparison

`stairs-v13-mesh.json` is ready for native comparison. SHA256 `fa1dd68fd3e87040a2e0d7b5fb72e41a8a939f11267a86d25be2c60e882c753c`, 64,780 triangles, 90 stones. The final matched stair images were directly inspected: no missing blocks, broader unequal nose losses and wider staggered joints are visible. Technical checks passed; Unity visual adoption remains pending.

The eight `localized-masonry-v13-*.json` architecture files are ready for selective native comparison. Final matched portal images were directly inspected: the rejected C-shaped middle-edge notches are gone; finite unequal corner losses interrupt eight specific pier/buttress/spandrel blocks. General V12 blocks, placement, scale and materials stay unchanged. The improvement is local and does not establish a whole-portal realism gain.

Final independent validation passed for all nine meshes: positive cross-dot-normal, no degenerate triangles, unit finite normals, exact identities, preserved source hashes and closed build outputs. The stair hash is unchanged from its reviewed image run. Architecture totals 6,950 triangles, retaining 99.612–99.881% of its matching V12 stone volumes. See `SELF_REVIEW.md` and `INTEGRATION.md` before integration.

The rejected middle-edge notch result is preserved in `rejected-repeated-notch-pass2`; it must not be confused with the root-level final eight JSON files.

The earlier missing-stone pass remains preserved in `rejected-empty-stair-pass1`. Welding alone did not fix it. The solver comparison and stronger per-stone checks are documented in `BOOLEAN_DIAGNOSTIC.md`; the final staircase uses Blender's Manifold solver on welded closed inputs.
