# Candidate49 — coherent reflected environment

All four actual Unity views were opened directly at the established resolutions. Shader errors0/runtime errors0/missing scripts0,109 reflection updates. This is a diagnostic; latest independent verdict remains candidate41:6.0/Tier2.

The reflection camera now uses the same OvercastStoneEnvironment cubemap radiance as the stone IBL, while the main camera's distant background remains intact. Actual flame/geometry radiance is not scaled. This removes much of the pale blue cloud-like wash apparent in48. Pools remain shallow and quiet, but the whole floor now reads too dry and weakly reflective compared with the target. This is useful environment coherence, not finished wet stone.

The point-light water lobe is narrower (.035/.10 rather than .07/.24), with small animated surface-normal slopes. The large flat warm patch persists; it is not fully explained or fixed by that lobe.48 raw-reflection evidence shows actual reflected fire clipped by raised stone near the main bright core, plus geometry reflections. CPU center intersections confirm coverage1 at both flames and partial nearby stone protrusion; broader emitter-footprint diagnosis is pending.

Opaque paving, stairs and contact meshes now use One/Zero blending because their shader alpha is always1 at their actual bounds. Other stone retains its height/distance fading. The same-image performance effect is unmeasured on49.

Large photo-aligned slabs, lower cap fan shading, uneven cape folds and the ContactV14 groups remain. Dominant unresolved issues are weak cool wet glints, locally clipped warm reflection, banded stairs, and dark regular architecture. Further material work is required before a prepared fresh independent submission. No49 player build/performance/motion result yet;48 results are not49 measurements.
