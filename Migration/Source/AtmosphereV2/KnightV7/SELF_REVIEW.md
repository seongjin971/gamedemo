# KnightV7 direct source review

Status: READY_FOR_NATIVE_COMPARISON. Source generation, independent data checks and all six actual matched renders passed. This is a bounded cape art derivative, not whole-character or reference acceptance.

I directly inspected concept.png, candidate46 zoom.png, then whole-before/after.png, cape-before/after.png and side-before/after.png. The before cape has shallow, almost parallel lower relief. The after cape has three unequal spreading ridges with a deeper central trough and a more legible left/right division in the whole view. The upper-central diagonal is shallow and visible mainly in the close view; it should not be assumed visible at the roughly 140-pixel native character scale. The revised hem is unequal without a torn or sharply serrated outline. Side comparison shows added rearward cloth depth and a continuous shoulder attachment, with no visible body intersection. Armor and helmet are visually unchanged.

The result remains relatively smooth, heavy cloth with the inherited static backward hang. It does not reproduce all fine folds or the leaner figure in the concept. Native lighting is much darker than the neutral preview rig, so final scene-size readability remains an integration check. No physics simulation or equilibrium claim is made.

## Verified scope and measurements

- Cape width: 0.7137879133 m before and after, exactly retained. The upper 14% UV attachment band is position-exact (3,234 duplicated export vertices).
- Three unequal authored fold amplitudes: 0.034, 0.058 and 0.043 m; maximum combined rearward displacement: 0.0711298585 m. Shallow diagonal amplitude: 0.013 m. No global smoothing or periodic groove pass.
- Measured left/right hem height-change difference: 0.0714000463 m, 10.003% of cape width. This is height asymmetry with a small interior lateral drift; the outer width is not expanded.
- Cape: 7,736 triangles and 23,208 loop-export vertices, unchanged. Polygon topology, UV buffer and native index buffer are exact.
- Native-local bounds in meters: X [-0.3924098313, 0.3213780820], Y [-1.0004991293, 0.0013137066], Z [-0.5188644528, -0.0196199864]. Existing object and parent transforms remain unbaked.
- Actual cape/body triangle intersection pairs: before 0, after 0, newly introduced 0. This checks the static inherited body meshes, not animation or collision-response behavior.
- All six other JSON mesh records are exact; every other Blender mesh including normals and all object parents/transforms/material slots are exact. The helmetV6 supplemental JSON is byte-identical. Protected KnightV6 files retain their original hashes.
- Independent native cross/dot QA: all eight main-plus-helmet records finite, valid indices, nonzero areas and strictly positive face/mean-normal alignment. Cape minimum alignment 0.7094216232; minimum triangle area 0.0000268175771 m²; maximum unit-normal error 1.1564e-7.

## Handoff

Use knight-v7-unity-meshes.json with the same seven-object importer mapping. Only Heavy_folded_crimson_cape positions and normals change. Keep the existing helmetV6 supplement; the copy in this folder is identical. Native conversion is (-BlenderX, BlenderZ, -BlenderY), with one winding reversal already applied. Do not convert again. All Unity integration remains with the root.

JSON SHA256: cba8df68b55fca9cdedb15346651adee4ded5fe8f91c26e7ed46ad2db2204be9

Blend SHA256: ab39f38eb6896044ee48eb323ee4b2e8a978332028d2f0e85ed10ba7dfffb9cb

Helmet supplement SHA256: e57503a85be1d6d67870e9dee425d4ff2a98e712cf89be5cbdc42a9982c9c2fe
