# Local masonry V13 self-review

The final matched stair and portal clay images were opened directly at 1536×1024. Source work is ready for selective native comparison. This is not whole-scene visual adoption, a Unity judge score or proof of Tier3.

The staircase keeps ninety stones, ten levels, the outer silhouette and all joint center positions. Thirty noses show broader unequal small losses; internal joints widen from 1.6 to 2.8 cm so the existing stagger is more legible. Large modular tread/riser planes remain. The final stair SHA256 is `fa1dd68fd3e87040a2e0d7b5fb72e41a8a939f11267a86d25be2c60e882c753c`, matching the separately reviewed stair render. See `STAIR_SELF_REVIEW.md` for its visual limits.

Eight particular portal pier/buttress/spandrel blocks receive local changes. The final version cuts unequal open top/bottom corners and adds shallow face flakes. It preserves the V12 reduction of continuous broad shoulders on the rest of the wall. The whole portal remains visibly modular, and many original faces are still regular. These selective cuts are deliberately a small intervention; the clay render does not support claiming that the cleaner/blockier native41 regression has been fully resolved.

The preceding portal pass was rejected after direct review because its middle-edge cutters created repeated C-shaped notches. The final matched after image removes that new motif; varied corner endings now interrupt the silhouette locally. The final context excludes the separate non-instanced arch ring and trim, so this preview is not a recreation of the complete native portal.

Technical checks passed on the actual final exports: 64,780 staircase triangles and 6,950 triangles across eight normalized architectural overrides; no nonpositive normal dots or degenerate triangles; finite unit normals; closed meshes after welding; exact original instance identities; unchanged V11/V12 source hashes. Every stair retains 98.434–99.424% of its original volume and the same connected-component count. Every architectural override retains 99.612–99.881% of its corresponding V12 volume and stays in normalized bounds [-0.5,0.5].

No Unity file, material, scene, shader or previous source version was edited. The candidate41 lighting audit remains relevant: neutral single-material stairs can still produce strong warm risers and cool treads under opposing lights and orientation-dependent wetness/GI. Parent must inspect the actual combined Unity image, movement and performance. Geometry import success cannot close that rendering issue.

Rejected evidence remains under `rejected-empty-stair-pass1` and `rejected-repeated-notch-pass2`. The empty-stone failure and the stronger per-stone export gate are recorded in `BOOLEAN_DIAGNOSTIC.md`.
