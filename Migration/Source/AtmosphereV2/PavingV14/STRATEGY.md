# Paving V14 bounded decision and provenance

The actual concept and candidate47 full were opened side-by-side before this implementation decision. The concept places greater weight on large angular rectangular slabs and restrained edge relief. Candidate47 has coherent neighboring stones, but too many smaller rounded pads, strong dark outlines and some smooth/triangulated cap highlights. Cap normal smoothing alone cannot resolve that silhouette or size mismatch.

Root authorized three connected changes in a new source version, preserving the fixed V13 mesh and all original maps:

1. Increase the photographed horizontal period from9.2 ×4.6 m to12.4 ×6.2 m, rebuilding contours, source-height sampling and every material UV together. This is an additional1.347826x art enlargement relative to V13 and total5.391304x relative to the source's published2.3 ×1.15 m area. It is not newly measured photogrammetry. The original92 source contours remain, with no arbitrary shrink, shuffle or random UV offset. Expected closed body count is450–550 instead of866.
2. Preserve nominal32–52 mm major-stone shoulders (and narrower subordinate shoulders) but multiply systematic perimeter drop by0.75. Independent per-stone plane levels, tilts and bounded2.8 mm scan residual remain. The vertical amplitudes are art direction, not measured source height. The purpose is to reduce repeated raised-pad rims while retaining physical fractured stone relief.
3. Area-weight cap triangle normals within each separate body only. An explicit cap face attribute survives triangulation. Internal cap loops receive the averaged normal; the cap perimeter stays hard against the bevel, and sides/bottom remain flat. No averaging crosses stones or flattens the whole floor to Y-up. Actual preview and strict positive face-normal tests must verify this, rather than assuming smoothing is an improvement.

The former whole-ground bounds, front coverage rectangle and rear staircase void bed remain. Ground stairs/upper landing are not edited. Independent water remainsY=-0.004; collision ground remains root's contract. Contact14 horizontal pockets must be measured/reprojected against the final frozen V14 top geometry because the larger source period changes local heights.

`prepare_sources.py` prepares only new scripts and an identical copy of the92 source guides. `build_hybrid_v14.py` is the canonical Blender build. The original maps are referenced read-only from PavingV11/maps. Source hashes include the preserved candidate47 V13 mesh, V11 inputs and map bytes. All UVs explicitly use12.4 ×6.2 m; source maps themselves remain unchanged.

Budget target below120k triangles, hard maximum141k. Existing strict gates remain: positive face/normal dot for every triangle, finite unit normals, no degenerate triangles, every body closed after position welding, positive volume, projected-top/footprint area agreement within0.00001 m², exact source UV and whole-ground bounds. Geometry-only build precedes independent exported QA; preview requires a matching passed QA hash. Before/after full/close Blender neutral and actual4K textured images must be directly inspected before native handoff.

Execution is queued after Contact14 and root's47 motion/DX11 comparison. No Blender or heavy array evaluation starts until root's explicit release. A numeric pass is not final native appearance or FPS acceptance.
