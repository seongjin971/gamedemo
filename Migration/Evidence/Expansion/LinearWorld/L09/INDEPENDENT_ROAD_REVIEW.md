# L09 independent road visual review

Date: 2026-09-11. Reviewer: fresh independent visual judge (`road_l09_judge`).

**Verdict: meaningful visible improvement, suitable for user review; 7.3/10 against the road-only target. Below an 8/10 target-match threshold. This is not final user acceptance.**

## Evidence and scope

I directly inspected the original image files with `view_image`:

- Target: `.dream-loop/linear-road/targets/path-transitions.png` (three-panel target artwork, not an implementation capture).
- L09: `capture/road-46.png`, `road-50.png`, `road-85.png`, `road-126.png`, `road-176.png`, `road-182.png`, `road-215.png`, `road-234.png`, `road-238.png`, and `road-244.png` under this report's directory.
- Corresponding same-position images under `Migration/Evidence/Expansion/LinearWorld/RoadBaseline/capture/`.

Judgment covers road surfaces, their visible edges, wetness, snow cover, and material continuity. Target panels have a tighter/different crop than the full Unity screenshots; no penalty is assigned for that crop difference. Composition below means the road's width, edge shape, continuity, and fit into the ground. Trees, rocks, character, overall scenery composition, gameplay, performance, and audio are outside the score.

I did not inspect implementation code, run builds, modify implementation, or receive any previous independent score. Static frames cannot establish absence of temporal popping while moving. The baseline's provenance as the unchanged L06 reproduction was supplied by the parent; this review verifies visible differences between the supplied images, not scene-file identity.

## Score

| Road criterion | Score | Reason |
| --- | ---: | --- |
| Composition | 2.5 / 3 | Road remains legible and edges now merge substantially better into earth and snow. The geometric slab outline and narrow stepped snow endpoint are removed in these views. Late-snow exposed patches still break up the traveled surface more strongly than the target. |
| Lighting | 2.4 / 3 | Road responds coherently to the existing sun/shadow and cooler rainy/snowy illumination. No obvious separate bright road layer remains. The target has more localized wet highlights and clearer material depth; these are weak in the current rainy surface. This score does not authorize changing scene lighting. |
| Materials | 1.9 / 3 | Earth, smaller old stones, dark wet ground, and increasing snow coverage now form a related surface family. Stones remain fairly uniform in value/shape at normal viewing distance; wet mud, pooled water, slush, and compacted snow are not sufficiently distinct. |
| Details | 0.5 / 1 | Smaller stones and uneven coverage provide useful detail. The target's angular chipped stone variation, gravel embedded in mud, small water-filled depressions, and granular compressed snow are only partially represented. |
| **Total** | **7.3 / 10** | **Road scope only.** |

## Visible change versus baseline

**Earth to old stone, road 46/50/85:** The baseline reads as a large tessellated paving strip with conspicuous dark joints. L09 replaces that with dirt-dominant stretches and smaller stone clusters, then a more continuous old-stone road. The transition is substantially less like switching manufactured tile sets. There is no visible straight seam at 46/50. Its remaining weakness is the contrast between broad smooth dirt areas and concentrated cobble islands, with little intermediate gravel; at 85 the cobble field becomes fairly uniform again.

**Rain, road 126/176/182:** The baseline changes between rectangular blocks and large polygonal blocks, visibly including both arrangements around the transition. L09 maintains the same smaller irregular-stone vocabulary across these views, with darkened earth between the stones and softer shoulders. The original conspicuous square-to-polygon road-type swap is not visibly present in the inspected L09 frames. This is a major improvement. However, the wet treatment still reads largely as dark gray/brown cobbles. The target's glossy puddles, muddy infill, and distinct wet stone faces are much easier to read. Existing rain streaks and ripple circles alone do not make the road material convincingly waterlogged.

**Early snow, road 215:** The baseline's clean stone ribbon, rectangular segment shoulders, and abrupt contrast with surrounding snow look laid on top of the terrain. L09 has feathered snow encroachment and partly obscured stones. It fits the setting considerably better. The mostly continuous dark stone center still looks more cleared of snow than the target's churned slush/packed-snow center; snow variation here is dominated by broad coverage patches.

**Late snow and taper, road 234/238/244:** The baseline visibly narrows through straight-edged segments and ends in a transverse cut. Those obvious geometric steps and the rectangular endpoint are gone from L09 in these images. Exposed road instead breaks into irregular patches while the faint snowy track continues. This directly addresses the most artificial original termination. Remaining gap: several large exposed-stone islands, including the conspicuous curved patch visible ahead at 234/238 and under the character at 244, alternate with broad pale gaps. The result reads as isolated melted/cleared spots more than one continuously traveled, compressed, dirty-snow path. It is still clearly preferable to the baseline cutoff.

## Meaningful gaps to the target

- The target uses a wider distribution of angular stone sizes, broken faces, irregular gaps, and tiny ground particles. Current stones read more like a similarly sized, low-contrast cobble texture, especially at 85 and in the rainy views.
- Target rain has visibly separate muddy areas, pooled water, and wet stone tops. Current rain has a coherent cooler/darker tint but weak water-versus-earth-versus-rock separation.
- Target snowy road retains continuous granular wear, dirty compressed snow, and small exposed stones along the route. L09's larger bare patches plus relatively clean intervening snow provide less convincing slush/compaction continuity.
- Current road edges are much improved, but some dark soft shoulders and broad coverage bands look like a surface mask at normal viewing distance. Smaller asymmetrical interleaving would more closely match naturally buried edges.

No meaningful new road seam or geometric cutoff was found. The tradeoff in L09 is reduced paving contrast and a more fragmented late-snow surface; the first supports the requested naturalness, while the second still needs refinement to match the target. No whole-scene regression claim is made from this road review.

## Highest-value road-only improvements

1. Connect the late-snow islands with a restrained dirty, compressed-snow/slush band. Keep irregular powder encroachment and some exposed stone, but vary the bare patches at smaller scales and reduce the largest curved island. Preserve the existing snowy terrain and scenery.
2. Give rainy road depressions localized puddle/wetness response and muddy infill, with a few readable highlights on exposed stones. Avoid increasing gloss evenly across the entire route or changing global lighting.
3. Add variation between larger broken stones, small gravel, and earth within the road, particularly through the dirt-to-cobble transition. Preserve the achieved soft edge integration and continuous stone identity across the rain boundary.

These are suggestions, not authorization to broaden the package. L09 is already a substantial, easily visible improvement suitable for the user's direct review. It should be described as a road-transition candidate with remaining material gaps, not a completed target match, whole-scene quality pass, gameplay pass, or user acceptance.
