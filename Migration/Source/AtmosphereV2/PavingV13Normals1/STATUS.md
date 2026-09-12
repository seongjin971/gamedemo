# Normal-only derivative — code preparation only

Root requested this bounded comparison after candidate47. Native47 full was opened directly. The now coherent foreground is an improvement, but the outlines read as raised rounded pads and several caps look too smooth. Fine fan-like bands remain on some lit cap areas.

`prepare_cap_normals.py` is prepared and has not been executed at this checkpoint. No derivative mesh, derivative normal array, export QA result or preview has been generated. The frozen V13 source hash is `dd46aefd74c0470bfea77fee2d22df8c72a1d2d47a75d18e7e6944c0c8f87e3c`. All source meshes/maps remain unchanged. Root's capture/build/FPS window prohibits execution/export/render until released.

The proposed diagnostic groups adjacent cap corners by body plus exact position/UV and area-weights their geometry normals. Each stone is independent. Bevels, sides, bottoms and bed remain unchanged. Any cap/side shared index is frozen so the test preserves every position, index, UV, color and vertex count exactly. It asserts strict positive face-cross/normal dot on every triangle and equality of all frozen arrays before a separately named export.

This is a meaningful one-variable test for fan highlights. It is not expected to correct the rounded outline or physical pad relief, and can make an already smooth-looking cap appear smoother. Those structural impressions come from the actual contour/bevel/drop and scene lighting, which this derivative intentionally keeps fixed. Geometry shadows from the1–3 mm residual can remain even if normal-induced bands diminish. No rendered improvement is claimed from code analysis.

After root release, the script can first run without `--export` for an in-memory strict QA report. Only an explicit `--export` writes the new candidate after all checks pass. A failed derivative remains unexported; no index flips or relaxed gate are used. Actual preview/native comparison is a separate subsequent step.
