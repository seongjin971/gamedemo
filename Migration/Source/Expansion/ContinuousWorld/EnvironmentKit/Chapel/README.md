# Open-aperture chapel modules

Two Blender-authored modules with actual geometric holes, separate cut masonry, radial voussoirs and molded arch bands. They are not opaque wall planes with painted windows. All FBX geometry is explicitly triangulated; UV0 is ready for the parent's stone-atlas mapping. No Unity scene, shader, material, importer or collider changes are included.

`CW_ChapelLancetWall.fbx`: nominal width 6 m, height 7 m, actual maximum depth 0.592 m. Ground-center pivot. Unity aperture spans X -1..1, starts at Y 1.3, retains full 2 m width to spring Y 4.3, then points to apex Y 6.1. Thus the overall window opening is 4.8 m tall. Framing remains outside the opening.

`CW_ChapelEntranceArch.fbx`: nominal width 5 m, height 6 m, actual maximum depth 0.592 m. Ground-center pivot, no threshold. Unity opening is X -1.5..1.5 from ground to spring Y 2.3, then tapers to apex Y 4.0. A 3 m-wide path is completely clear below the spring; the upper pointed part is not a 3-by-4 rectangular opening.

Source coordinates are X width, Y depth, Z height. FBX is Y-up/-Z-forward, so Unity local X is width, Y height, Z thickness. Exact mesh bounds, arch radii, counts and 75 aperture-ray samples per module are in their manifests. `audit_chapel_modules.py` reimports exported FBXs and repeats all aperture and solid-wall ray checks, plus UV/triangle integrity. This verifies actual geometry without treating it as Unity navigation or user play acceptance.

The clean neutral contact render is `chapel-preview.png`; the parent's existing PBR stone atlas should replace preview materials `CW_ChapelStone`, `CW_ChapelStoneLight`, `CW_ChapelMortar`. The recessed mortar core prevents decorative block joints becoming holes. Culling/placement of near-camera walls remains the scene builder's responsibility.
