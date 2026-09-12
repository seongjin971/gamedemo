# Knight v3 mesh integration

Use `knight-v3-unity-meshes.json`. Its seven `objects` records each identify the exact existing Unity GameObject with `gameObjectName`. Assign a new Mesh to each matching MeshFilter; retain its entire Transform hierarchy, local position, rotation and scale. Preserve Renderer material assignments.

Fields are flat arrays: `positions` / `normals` in triples, `uv` in pairs, `indices` in triangle triples. Coordinates are already Unity (-Blender X, Blender Z, -Blender Y), and indices already reverse Blender triangle winding. Do not reconvert axes, flip UV, reverse indices again, or bake parent scale a second time. Use exported normals; calculate bounds and tangents after assignment. Every mesh is below 65,535 vertices.

Exact names:
- Icosphere004_rounded_v2 (Left_shoulder_pauldron steel)
- Icosphere004_rounded_v2_1 (Left_shoulder_pauldron thin rim)
- Icosphere007_rounded_v2 (Right_shoulder_pauldron steel)
- Icosphere007_rounded_v2_1 (Right_shoulder_pauldron thin rim)
- Heavy_folded_crimson_cape
- LeftArm_Polished forged edges
- RightArm_Polished forged edges

The last two reconstruct the original material-merged direct arm geometry with only the obsolete broad pauldron bars omitted. They preserve the elbow and finger plates. The replacement thin rim now follows each new shoulder plate, so no extra GameObject is required.

The source blend stays untouched. The candidate blend retains every original transform and parent. The two obsolete bars are retained in the candidate but hidden from rendering; all other source objects remain available. Mesh export includes no lights or cameras. Preview cameras/lights exist only in the render process and are not saved in the candidate blend.

The material assets were not changed. For scene integration, shoulder steel needs a restrained broad reflection rather than a point-like chrome glint; independently tune smoothness if necessary after live screenshot inspection. This asset replacement addresses silhouette and hanging folds, and does not establish whole-scene visual acceptance or runtime performance.
