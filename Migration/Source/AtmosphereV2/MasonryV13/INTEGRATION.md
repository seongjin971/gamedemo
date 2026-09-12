# Local V13 integration contract

This is a selective source experiment. V11 and V12 remain preserved. Unity scene/material/lighting changes belong to root.

`architecture-overrides.json` names exactly eight original bridge instances: portal pier, buttress and spandrel blocks. It includes original node UUID, original unfiltered instance index, material/geometry UUIDs, exact position/quaternion/scale/color, and the matching V12 source-variant index. Verify the bridge hash and all fields before replacement. Do not use the filtered selected-array index as the manifest index.

The replacement `localized-masonry-v13-0.json` through `localized-masonry-v13-7.json` files use normalized Unity-basis geometry. Preserve each original instance TRS, material and color. In `AppendStone`, apply an override **after** the normal `architecture[seed%6]` fallback would have selected its mesh, or skip that fallback for an explicit override. Do not allow the fallback to silently replace the override. Do not replace a whole node or all occurrences of its geometry UUID. Every other V12 instance remains unchanged.

`stairs-v13-mesh.json` replaces the existing one-piece stairs mesh at identity transform. It keeps all 90 stones and their ten levels, outer flight width and individual joint center positions. The original 278-part removal manifest remains exactly the V11 manifest; do not remove new scene objects by approximate coordinates. The stair material stays under root's shader/material investigation.

The original adjacent-row joint-center stagger was already 21.0-46.1% of nominal width, median 31.9%, measured across 72 adjacent-row joint pairs. The source did not lack lateral staggering. V13 leaves those centers unchanged and widens the interior gap from 1.6 cm to 2.8 cm, approximately 0.74 to 1.29 pixels at the candidate full camera. The same thirty selected noses receive broader unequal losses; new cut depths and vertical losses stay below 5 cm. Existing older local damage remains unless removed by the new cut. This does not claim all inherited chips have the same dimensions.

Portal clay comparison includes the matched instanced stone context, but excludes the separate non-instanced arch-ring mesh, trim and other scene elements. It is source geometry evidence rather than a recreated native frame. Stair clay comparison uses the existing V11 camera/light setup. Neither preview includes new scene lighting or material changes.

V13 cannot by itself solve candidate41's orange-front/blue-top pattern: the read-only audit established neutral per-stone RGB, one stair material, and strong opposing moon/fire illumination with additional orientation-dependent wetness/GI. Evaluate the local damage alongside root's lighting correction; do not report the shader issue fixed solely because an override imported.
