# KnightV7 cape-only source contract

This directory derives only Heavy folded crimson cape from the final KnightV6 blend and seven-record JSON. It retains the separate helmet-v6-unity-mesh.json byte-for-byte. Every other Blender mesh including normals, object name/parent/transform/material slots/visibility, and six non-cape JSON records must remain exact. Tree and Unity files are outside this package.

This is static art direction of an existing baked cloth mesh. It is not a new cloth simulation, converged physics equilibrium, animation or collision-response system.

The deformation preserves the upper14% attachment band exactly and adds depth in cape-local +Y, away from the inherited body. Three individually authored unequal curved fold paths spread toward different hem positions. A smaller diagonal ridge crosses the upper-central panel. The two solidified cloth surfaces use the same UV-domain deformation. No periodic groove function or global cloth smoothing is applied.

The cape's approximately0.714m X width is fixed. Hem asymmetry means an authored left-versus-right height difference change of0.0714m, about10% of that width, plus a small interior lateral drift. This keeps the broad envelope and object placement rather than scaling the character. Source polygon topology is unchanged; JSON uses the source triangle layout, UV buffer and index buffer exactly, with only cape positions/normals replaced.

Blender-to-native Unity conversion is (-x,z,-y), and winding reverses once as [0,2,1]. The JSON is already native-local. Do not reflect again, bake object scale into vertices, or change hierarchy/material assignments. Keep the existing helmetV6 supplement installed; the byte-identical copy here is preservation evidence and a complete handoff reference.

Run build_knight_v7.py with Blender5.2.1 --background --threads3. The builder checks unchanged attachment vertices and source bounds, exact other records/meshes/state, and actual mesh-body BVH overlaps before/after. New body overlap pairs stop export. validate_knight_v7.py independently checks native finite geometry, valid indices, nonzero triangles, unit normals, strict positive face/average-normal dot, exact other records/UV/index buffers and actual authored hem difference.

Run render_knight_v7.py separately after performance holds are released. It produces matched before/after whole, cape close-up and side views with identical original materials, cameras, lights, samples and exposure. Preview cameras/lights are not saved in the delivery blend. Final native material response and actual scene-size review remain with the root.

Final status: READY_FOR_NATIVE_COMPARISON. All six actual matched images were directly reviewed; see SELF_REVIEW.md for findings and limitations. The AWAITING_DIRECT_REVIEW build-report marker records the earlier generation stage. SELF_REVIEW.md records the subsequent completed review.
