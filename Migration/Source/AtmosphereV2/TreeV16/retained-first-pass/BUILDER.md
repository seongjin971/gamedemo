# TreeV16 source contract

Bounded derivative of final TreeV12. Only this new directory is writable. Original GLB, V11/V12 derivatives, Contact14, Paving15 and Unity are immutable inputs. No external generation API is used.

The three widest horizontal masses receive an 18% whole-cross-section field; its support includes the broad outer bark rather than only V12's narrow core. The selected projecting short bark sites retract with a smooth spatial field. No periodic noise, new twigs, global mesh smoothing or radial root enlargement is added.

Each root is parametrized along its existing outward centerline. The last 25% descends, reaching full descent at 90%. All sampled terminal vertices in the entire central 1.08-radian corridor must sit at least 3cm below actual Paving15 support, rather than matching one near-zero vertex. Three roots retain radial reach. The fourth root turns and retracts toward the real inward parapet; the current floor does not exist below its original outermost tip. The supported endpoint is checked against actual floor and existing parapet context. Positive spatial Jacobians and strict native orientation checks are independent from visual acceptance.

Run build_tree_v16.py with Blender5.2.1 background and 3 threads, then build_covers.py with the same executable. Run validate_tree_v16.py with Blender's bundled Python/NumPy. Render render_context.py only in a coordinated GPU slot. TREE16_ROOT_ONLY=1 limits the first diagnostic to the two root views; TREE16_SKIP_ROOTS=1 finishes the other six later. No script writes to Unity or original sources.

tree-v16-mesh.json is native model-local (-BlenderX, BlenderZ, -BlenderY), winding reversed once, with original per-triangle UVs and white vertex colors. Keep parent world origin (7.2,0,3.7), scale1.73, original parent yaw and mesh-local yaw-20. Never renormalize height or recenter from the hidden underside AABB. tree-v16.blend contains the tree asset before adding context or covers.

tree-v16-covers.json and tree-v16-soil.json are separate native WORLD-space identity meshes, using the existing Rock05-compatible material/vertex-color convention. Their conversion from context Blender is (x,z,-y), orientation preserved, so do not apply the tree's local reflection again. Existing Contact14 is preserved; overlaps with its small soil deposits must be reviewed in final native context. No automatic removal of older pieces is authorized here.

Matched Blender before/after context uses actual complete Paving15, Contact14 deposits/rubble and retained parapet geometry. Full, zoom and glare camera parameters come from the current native capture helper. The native screenshots remain the reference; this context render reproduces placement and camera but not the Unity shader/lighting stack. Equal roughness0.85 and dark wood tint are preview-only. All final delivery materials and photo UVs remain inherited.

Final nav must be rebuilt/audited from the actual installed tree plus new covers. The source-only root-navigation-evidence.json is evidence, not an automatically accepted collider. Root contact supports are invariant under the approved PavingV16 foreground patch, which is far outside this region.

Status: CODE_READY; no visual acceptance before actual generated previews.
