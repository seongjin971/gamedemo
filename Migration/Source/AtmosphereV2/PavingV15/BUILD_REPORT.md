# PavingV15: one confirmed obstructing stone lowered 11mm

This is a conditional source package following a flame-footprint diagnosis. Only `HeroScanSlab_280_bottom_left_large` moves. The left fire-reflection region, other 492 stone bodies, continuous bed, brazier foundations, and all earlier source versions remain unchanged. Root owns native integration and visual acceptance.

## Confirmed source obstruction

`diagnose_bright_footprint.py` samples the actual flame RGBA using linear-decoded bilinear RGB, sequential shader UV warp at time 2.3, the current core/radiance formula and material HDR color, actual serialized billboard centers/scales, and the imported quad's measured `X=.5-u, Y=v-.5` layout. Reflection-camera billboard vectors come from the mirrored source view matrix. Unity right is `cross(worldUp, forward)`; it is distinct from the imported quad's X reversal.

Each emitting sample is projected from its virtual reflected position to the Y=-.004 water plane. The script tests an exact triangle ray toward the camera against PavingV14, including vertical side faces, and evaluates the current wet-mask's bilinear red/max(U±.018)/smoothstep coverage. Sampling grid is 128x128; pixels below .02 emitted linear luminance are omitted. Bright core means shader core >= .5. Reported fractions are emitted-luminance weighted, not tone-mapped screenshot areas.

| View / emitter | V14 total luminance occluded by paving | V14 bright-core luminance occluded | V15 paving occlusion | Mask-only luminance loss, unchanged |
| --- | --- | --- | --- | --- |
| full / left | 0% | 0% | 0% | 2.84% |
| full / right | 27.93% | 18.49% | 0% | 0% |
| orbit / left | 0% | 0% | 0% | .80% |
| orbit / right | 0% | 0% | 0% | 3.72% |

All full/right occlusion comes from one stone. The source mask does not hide its bright full-view core. The stone occupied X [.07018,1.03535], Z [.59488,1.13846], with top Y=.0050505. It is over two meters in Z from the brazier centers at Z=-1.45. The new highest point is -.0059495, leaving >=1.9495mm clearance below the water.

An initial diagnostic used the wrong sign for the camera-right vector. Its preliminary 22.34% core / 29.77% total figures were explicitly withdrawn. Correcting to Unity's basis produced the table above; the same single occluder and zero-after result remain. The final reproducible script contains the corrected basis.

The source diagnosis does not include other scene occluders, runtime sprite deformation beyond the shader's documented t=2.3 warp, RT filtering/bloom, GPU mask mip derivatives, or tone mapping. Native paired raw-reflection capture remains the visual check.

## Exact geometry contract

- Output: `paving-v15-mesh.json`, world-space identity, Unity orientation already applied, white colors.
- SHA256: `630a8d5fcc54f38825fcdbf7fb401cd9768894d67b1b7d3e8b4f91cf329242ce`.
- Preserved PavingV14 SHA256: `00ee641f13bdc841a4d0fd531379380a33952ee8f952133e750380e9e4be5c59`.
- The selected body's 286 exported vertices receive only Y-=.011. Triangle-index range [231480,231888) is unchanged (136 triangles).
- All indices, UVs, colors, and normals match V14 exactly. All X/Z values and every other body's full positions match exactly. Translation has an identity normal transform, so retaining the original geometry-derived normals is correct.
- No UV/art-scale change: V14 period remains 12.4x6.2m with the original per-stone source attachment.
- Ground X bounds remain [-8.936228752,9.040660858], Z [-11.101970673,21.067903519]. Stair void/coverage remains exact.
- By explicit authorization, the moved body's buried bottom and whole-mesh minimum Y extend from -.115000002 to -.126000002. Whole-ground maximum Y stays .010417859. No mesh-AABB rescale or normalization occurs.
- Navigation Y=0 and independent water Y=-.004 are unaffected by this source package.

## QA and reproduction

`build_local_drainage.py` requires the expected source hash and a significant one-body obstruction diagnosis before export. It independently verifies the serialized final arrays, positive triangle-to-normal dot for all three normals of every triangle, nondegenerate geometry, and position-welded closed, consistently oriented bodies with positive volume.

Results: 104,872 triangles, 161,710 vertices; 104,872 positive triangles; zero nonpositive or degenerate triangles; 493 closed bodies; zero bad bodies. Unit-normal maximum error 1.70e-7. Rigid translation numerical error <4e-18m. `export-qa.json` contains exact evidence.

Run with system Python and Pillow:

```
python diagnose_bright_footprint.py
python build_local_drainage.py
python -c "import diagnose_bright_footprint as d; d.main(d.OUT/'paving-v15-mesh.json','after-v15')"
```

`before-v14-*` and `after-v15-*` occlusion PNGs are CPU diagnostic diagrams: red means paving-ray occlusion, blue means coverage below .5, green means visible. They are not native or Blender renders.

`render_previews.py` runs on the preserved `PavingV14/paving-v14.blend`, changes only the selected object's translation, and saves a separate `paving-v15.blend`. Actual Blender images are in `previews/`: matched native-ground, neutral-close, and textured-close before/after pairs. They inspect the small geometric change; they do not simulate Unity's planar reflection shader.

Direct review of all six actual Blender renders: the selected central elongated stone's exposed side becomes slightly shorter, its upper face stays planar and its photo grain stays attached. No new wedge, gap, or shading discontinuity appeared. At whole-ground scale the change is intentionally difficult to distinguish, consistent with a single 11mm lowering. The existing rounded source outlines and vertically stretched side UVs remain visible in the extreme close-up; this package does not address those prior limitations. Rendering finished at 2m15s, saved the separate blend, printed the expected final hash, and quit; the render slot was released.
