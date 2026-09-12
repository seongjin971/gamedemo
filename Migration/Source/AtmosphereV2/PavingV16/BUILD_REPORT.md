# PavingV16: ten-stone fracture-graph prototype

This is a bounded structural prototype, not a whole-courtyard rebuild or a reference-match acceptance. Root owns Unity integration, camera/materials/water, and native comparison. No Unity files or earlier source versions were changed.

## Scope and tracing

The selected V15 bodies are **96, 97, 105, 106, 107, 112, 131, 134, 144, 146**. Their exact names, raw photographic corner polygons, source IDs, connected fracture lines, and plane coefficients are recorded in `trace_graph.json` and `fracture-metadata.json`.

The original selected footprint was approximately X[-4.082,-.376], Z[6.231,10.301]m. The final new components occupy X[-4.111133,-.351172], Z[6.236328,10.323242]m. The small differences restore the original traced corners instead of the old averaged contours. No outline or local fill overlaps another stone's footprint. Local fill extends at most 70mm outward from its selected source edge and 3mm inward beneath that same stone.

This is well separated from the V15 confirmed drainage stone280 at X[.070,1.035], Z[.595,1.138] and from the brazier foundations. That stone's geometry, the other 482 unchanged original stones, the entire original bed, navigation Y=0, ground extent, and stair void retain their original records.

Source coordinates use the original Tiles130 Color/AO reference at 2048x1024 with top-left origin, matching the unmodified 4096x2048 maps. Tile shift is [-12.4,6.2]m. The polygons are the existing manually traced photographic boundaries with their original acute corners. No perimeter averaging, random UV shift, or source reordering is applied.

The primary line endpoints come from those photographic boundary corners/notches. Their continuation across an interior face and their vertical lithic angles are **authored interpretation**, not a claim that every line is a photographed dark crack or a measured scan elevation. This distinction is explicit per stone in `trace_graph.json`. Ten original source units remain ten connected bodies rather than being broken into a scatter of independent pebbles.

## Different construction method

- One or two explicit break lines divide each cap into connected piecewise planar regions. Actual mesh edges run along those lines. Geometry normals remain separate at plane changes; arbitrary fan triangles do not define the intended fracture shape.
- The former whole-loop inset and continuous shoulder are removed on the selected stones. Only specific source boundary segments receive a one-segment 16mm or 29mm chamfer. Other corners and stepped outlines remain angular.
- Planes use small authored slopes, with the existing per-stone tilt as their base. Heights are checked at actual fracture intersections, not only polygon corners, and new tops remain <=.0095m. Original water Y=-.004 is unchanged.
- Ten sparse soil infill bodies follow the original global photo UV. Their inner middle approaches the selected stone's underside; both ends and the outer edge taper 1mm below the exact old bed ray height. This removes the first pass's exposed rectangular fill end faces. The original bed mesh itself is untouched.

All original vertex records are kept as an exact prefix. Only the ten original selected part index lists are omitted, and the replacement stone/fill vertices and index lists are appended. Old selected vertex records become unreferenced; this deliberately avoids renumbering or rounding unrelated source data.

## Frozen native source

`paving-v16-mesh.json` uses world-space identity, `alreadyUnity:true`, standard positions/normals/UV/indices/colors arrays and the established positive face-cross/normal orientation.

- Final SHA256: `f812feed57a6b6e2fa3c7378caada08243c650883b5e1f33d630640dd828b7b6`.
- Preserved V15 SHA256: `630a8d5fcc54f38825fcdbf7fb401cd9768894d67b1b7d3e8b4f91cf329242ce`.
- 104,058 triangles, versus V15's 104,872; 163,924 exported vertices, including the preserved old prefix.
- New source objects: ten replacement connected stone bodies and ten closed soil fills.
- Exact whole-world bounds remain X[-8.936228752,9.040660858], Y[-.126000002,.010417859], Z[-11.101970673,21.067903519]. No AABB renormalization.
- UV period remains 12.4x6.2m, with `u=x/12.4, v=z/6.2` on every new surface. Maximum exported UV consistency error is 5.81e-8. Original map pixels and material source assets remain untouched.

## Independent validation

`validate_fracture_graph.py` reads the serialized JSON independently of Blender. It checks all triangle normals, finiteness, indices/vertex prefix preservation, new-body welded edge incidence/orientation/positive volume, projected cap area against original raw polygon area, exact UV registration, full bounds, and polygon intersections with all neighboring stones.

Final results: zero nonpositive triangle-normal pairs, zero degenerate triangles, zero nonfinite new attributes, maximum unit-normal error 1.70e-7. All twenty new bodies are closed and consistently oriented with positive volume. All ten caps preserve their intended projected area within 1e-5m². Exact neighboring outline/fill overlap count is zero. Every unchanged part's triangle index list and every original vertex record match V15 exactly.

The first preflight found two numerical bisect slivers; 2-micrometer duplicate/degenerate topology cleanup removed them without relaxing winding gates. A later stronger footprint-intersection check rejected two first-pass fills that the original point-probe test missed. The complete first pass, its failed QA and eight actual renders are preserved in `rejected-first-fill-pass/`. Final intersection testing uses complete edge crossing plus containment, and both offending fills are omitted.

## Reproduction and evidence

1. Open the preserved V15 blend in Blender and run `build_fracture_graph.py`.
2. Run system Python `validate_fracture_graph.py`; require `passed:true`.
3. Open the new V16 blend and run `render_previews.py` in a coordinated render slot.

`previews/` contains paired actual Blender neutral/textured **full** and **zoom-patch** views. The final after-only batch reuses the exact unchanged first-pass `before-v15-*` PNGs and rerenders the four final after images. Source materials and cameras are matched within each comparison; these are not certified pixel-identical native Unity captures. The previews do not simulate Unity's separate water shader.

The prototype changes the local outline and plane topology. It does not replace the remaining rounded source contours across the courtyard, the enlarged source grain, or Unity's light/reflection response. Full-scene and native lighting checks must decide whether this method warrants the separately proposed 20–30-hero expansion.

## Direct final review

All final actual full and patch views were opened directly, alongside their matched before images. In the neutral full view the ten-stone area has a visibly more angular edge sequence than the neighboring old rounded units; its limited size means the courtyard as a whole still reads mostly as V15. In neutral zoom, pointed corners and selective chamfers replace continuous rounded shoulders, and the final soil tapers no longer look like small rectangular support plates. Textured full/zoom retain the source-photo registration and show no newly shifted crack pattern.

The internal plane changes are restrained under this diffuse Blender lighting. They should be checked under native moon/fire specular lighting before describing them as a decisive lithic-surface match. Some long edges remain clean, and the original photographed grain remains enlarged. This package is technically ready for a bounded native prototype comparison, not a claim that the reference's whole-floor structure or target score has been achieved. No expansion is included.
