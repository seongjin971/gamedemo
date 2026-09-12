# Dense fine golden reed band

`CW_GoldenReedBand4m.fbx` contains480 fine bent stems, narrow drooping leaves and69 slim seed heads. No broad green rosettes, alpha cards or whole-plant billboards. Exact full bounds are4m along sourceX by1.5m sourceY by1.2m sourceZ; pivot is ground center. Preserve imported -90 degree X root conversion. Place bands in overlapping natural curves along rock-water contacts.

LOD0 is9,846 triangles. `CW_GoldenReedBand4m_LOD1.fbx` is4,570 triangles /240 stems, in the same coordinate basis. Its internal node is intentionally named `CW_GoldenReedBand4m_Reduced` to avoid Unity's orphaned `_LOD1` naming warning; filename stays unchanged. Final FBX reimport verifies both files: explicit triangles, zero degenerates, UV0..1 and source alignment.

Use authored solid colors, without atlas binding: `CW_GoldenReedStem` (.54,.41,.18), `CW_GoldenReedLight` (.72,.57,.29), `CW_DryReedLeaf` (.43,.37,.19), `CW_ReedSeed` (.37,.26,.115), roughness about.92. Thin leaves should use Cull Off / two-sided rendering; stems are real triangular tubes. The density and warm fine-stem silhouette were checked in `reed-band-preview.png`. Parent retains final scene shading/placement and performance verification.

`generate_reed_band.py` reproduces both assets and already includes the corrected node naming. `fix_lod_node_name.py` records the one-time naming-only export correction. Source blend, scripts and renders remain outside Assets. No existing assets or external-service credits were used.
