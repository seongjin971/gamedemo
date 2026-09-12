# Preflight history

No V13 file has been imported to Unity at this checkpoint.

1. The first source contour preflight passed, but actual clipped/AO-refined geometry found a 5 mm remnant edge at the world coverage boundary. The cap inset folded at that remnant. `inset-failure.json` retains the failing polygon. Boundary cleanup now removes consecutive remnants shorter than 25 mm before constructing the stone body; the underlying exact coverage bed is preserved.
2. The next export found 8 face/normal disagreements. Explicit body triangulation before computing geometry normals and an added independent projected-top/footprint check exposed a folded bevel strip on `middle_left_upper` (projected area 0.1263709227 vs footprint 0.1263427590 m²). The strict 0.00001 m² area tolerance was retained.
3. Each bevel strip is now required to remain convex in XZ before any mesh is authored. The local contour inset scales down where necessary, rather than accepting folded strips or reversing indices to hide them. Both cap triangulation area and the complete body's projected area must agree with their polygon areas.
4. A subsequent geometry preflight was deliberately interrupted for root's candidate46 Unity capture slot. It did not produce a final QA/preview result. The next workflow uses `--geometry-only`, then independent JSON validation, then a separate preview script which requires a matching passed QA hash before rendering.
