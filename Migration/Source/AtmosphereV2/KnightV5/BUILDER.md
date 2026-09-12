# Art-directed cloth v5 candidate

The top-level `knight-v5.blend` and `knight-v5-unity-meshes.json` contain the art-directed baked cape, not the contracted raw simulation. The complete seven-object JSON retains the six other records exactly. Keep all GameObjects, Transform hierarchies and materials. Coordinates and winding are already Unity-compatible, exactly as in the tracked v3 pack; do not reconvert them. Recalculate bounds/tangents after assignment and use exported normals.

This is a physics-derived, art-directed cloth mesh. Three raw Blender cloth attempts are preserved in `attempt-01-contracted`, `attempt-02-stiff`, and `attempt-03-flared`. All failed the original broad silhouette requirement. The raw final simulation also retained approximately 5 cm maximum vertex movement across its last ten frames; it is not certified as a converged static equilibrium. Do not integrate a raw attempt.

The approved follow-up approach restores the v3 broad envelope by corresponding grid row while retaining the simulated nonperiodic relief and small lateral drift. A low-pass filter removes fine collar crumples, and shallow unequal hem sags are sculpted afterward. No periodic longitudinal groove function is used in the final displacement. `art-direction-report.json` records raw and final bounds and explicitly marks the result as an art-directed candidate.

Reproduce from this directory:

```text
blender --background --threads 6 --python simulate_cloth.py
python art_direct_cloth.py
blender --background --threads 6 --python finalize_cloth.py
blender --background --threads 6 --python render_preview.py
```

The art-direction script intentionally reads the preserved final raw cage in `attempt-03-flared/settled-cage.json`, ensuring deterministic export. `simulate_cloth.py` can recreate the authoring run for inspection. `cloth-v5-authoring.blend` holds the pinned wide rest pattern, cloth settings, collision proxies and steady air effector at the starting frame. The final candidate blend is reloaded from pristine v3 and receives only the baked cape; none of the authoring proxies, wind objects or simulation modifiers enter it.

`finalize_cloth.py -- --source-dir /path/to/Knight` supports an external source directory containing the original v3 blend/JSON. Simulation and rendering scripts currently discover the repository source directory. The preserved cage plus art-direction and finalize scripts are enough to recreate the exported candidate without rerunning physics.

Final cape: 7,736 triangles, 23,208 exported loop-corner vertices. Source hashes, exact six-record preservation, all other Blender meshes, transforms/parents, materials, finite values, valid indices, unit normals and bounds are verified in `export-validation.json`. Studio previews use an identical camera/light rig. No Unity integration, runtime test, animation work or final scene acceptance was performed in this package.
