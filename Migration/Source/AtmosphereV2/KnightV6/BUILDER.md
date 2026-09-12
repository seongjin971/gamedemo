# Knight V6 integration contract

This directory contains a seven-part replacement pack and a separate helmet
supplement. Consult `SELF_REVIEW.md` and `export-qa.json` before consuming them.

`knight-v6-unity-meshes.json` retains the exact seven V5 GameObject names and
record order. Only `Icosphere004_rounded_v2` and `Icosphere007_rounded_v2` shoulder
steel records are replaced. The cape, both thin shoulder-rim records, and both
arm-trim records are copied exactly from V5.

`helmet-v6-unity-mesh.json` is a separate one-object pack for the existing
`Angular_closed_bascinet` GameObject, under the existing `Head` transform. This
is an existing object replacement, not permission to create another helmet or
change its transform/material. Its original Unity import object id is
`2507cff0-bb1f-4e6e-802a-38e85ddda457`, and original parent id is
`280be315-6128-47ac-988d-3a693604496e`. Material id stays
`f7d20fcf-c1c0-4764-a247-8511f3551f90`.

Every mesh is already in the working Unity `(-Blender X, Blender Z, -Blender Y)`
coordinate basis with triangle corners reversed once. Apply exported positions,
normals, UVs and indices directly, preserve all existing hierarchy, transforms
and material assignments, and calculate bounds/tangents after mesh assignment.
Do not reflect again or bake the object scale into vertices.

Reproduce with Blender 5.2.1:

```text
blender --background --threads 6 --python build_knight_v6.py
python validate_knight_v6.py
blender --background --threads 6 --python render_knight_v6.py
```

Rendering is separate so it can be held during exclusive runtime benchmarks.
It uses identical original materials, camera, light rig, samples and exposure
for V5 and V6. Preview lights/cameras are not saved into the candidate blend.
Root retains responsibility for native metal roughness and scene acceptance.
