# W03 independent visual verdict

Date: 2026-09-11. Reviewer: fresh Dream Loop Pro visual judge subagent. Read-only review except this verdict. The installed `dream-loop/SKILL.md` and linked Pro workflow were read. Appearance was judged by direct `view_image` inspection of all four supplied target images, all seven requested W03 raw Unity captures, and all seven corresponding W01 captures. W01's verdict was used to maintain scoring consistency. No implementation code, labels, or numeric pixel statistics were used to infer visual success.

Targets: `.dream-loop/weather-world/targets/01-prestorm-forest.png`, `02-default-distant-flash.png`, `02-rare-strong-flash.png`, `03-night-blizzard.png`. Targets are 2688 x 1520 and were displayed at 2048 x 1158 by the image viewer; the submitted Unity captures are 1920 x 1080. Framing is compared proportionally, without claiming pixel registration.

**Full target fidelity: 5.775/10, displayed as 5.78/10. W01 was 5.4875/10, displayed as 5.49/10. Improvement: 0.2875 points. W03 remains below the Pro 8/10 visual exit threshold.** Visible snow streaks and a brighter distant flash region improve specific weather features, but the remaining snow lighting, storm depth, and flash integration defects prevent a visual pass. The default flash also introduces an obvious pale/translucent foliage appearance in the upper-right distance.

This is a full-image fidelity score, including inherited scene differences. It is not a weather-only score and must not be relabeled as weather acceptance. Timing, motion, FPS, audio, traversal, preservation audits, and final user acceptance require their own evidence.

## Scores

| Target | W03 evidence | Composition /3 | Lighting /3 | Materials /3 | Details /1 | Total /10 | W01 total |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 01 prestorm forest | `capture/weather-84.png`, `capture/weather-104.png` | 1.80 | 1.75 | 1.35 | 0.30 | **5.20** | 5.20 |
| 02 default distant flash | `capture/abbey-distant-flash.png`; normal context `capture/weather-198.png` | 2.60 | 1.75 | 1.25 | 0.30 | **5.90** | 5.65 |
| 02 rare strong flash | `capture/abbey-strong-flash.png`; normal context `capture/weather-198.png` | 2.60 | 1.65 | 1.40 | 0.30 | **5.95** | 5.95 |
| 03 night blizzard | `capture/weather-323.png` primary; `capture/weather-282.png` supporting approach | 2.50 | 1.45 | 1.70 | 0.40 | **6.05** | 5.15 |
| Equal-weight average | Four target totals | 2.3750 | 1.6500 | 1.4250 | 0.3250 | **5.7750 (5.78)** | **5.4875 (5.49)** |

Forest and strong-flash scores are unchanged because their visible target discrepancies remain materially the same. Default-flash lighting gains are partly offset by the new foliage appearance. Blizzard lighting/details improve, but its player and surrounding landmarks are also framed higher than W01 and the target; composition drops 0.15. No material improvement is awarded merely because a brighter particle field covers a surface.

## Weather defects in priority order

1. **The snow area still has clear-weather illumination rather than the target's diffuse night storm.** W03 is visibly darker than W01, so that correction receives credit. However, both the approach and deep pass retain broad, relatively bright blue snow planes and highly legible tree-shaped cast shadows. The player shadow is also long and conspicuous. The target has darker slate-blue midtones, more atmospheric loss, and softer integration of shadows into drifting powder. Rework the snow zone's balance of direct light, ambient fill, and depth haze; do not keep lowering every object equally until trees/player become black cutouts. Preserve local player/road separation and the accepted normal-rain darkness. The remaining issue is a combination of lighting and air, not just one exposure value.

2. **The snow now communicates wind, but reads as a repeated streak field rather than a layered blizzard.** Many W03 streaks are narrow, hard-edged, bright, and almost horizontal, with similar contrast and apparent scale across the upper distance, tree crowns, road, and foreground. Several slash directly across the player silhouette. The target's streaks have a stronger diagonal tilt, many softer and finer marks, a wider range of lengths/opacity, and broad broken translucent powder plumes. W03 lacks those broad veils and has little convincing distance-dependent obscuration. Build a depth hierarchy: fine low-contrast distant snow, varied middle streaks, a limited number of larger soft near flakes, and irregular drifting powder volumes crossing different scene depths. Avoid increasing all streak counts/brightness together. Their static shape makes sideways wind plausible; actual velocity, gust coherence, and motion quality are not proven by these frames.

3. **The distant flash reveals a new foliage integration defect.** In W03 `abbey-distant-flash.png`, the large upper-right tree group becomes washed-out gray/pale foliage with dark skeletal branch lines and visible card-like leaf masses. Nearby grass in the illuminated area also retains conspicuously dark cutout outlines. The target has luminous air behind/distantly around foliage while the canopy preserves a convincing dark mass and natural surface response. This appearance is absent from W01's more uniform default flash and is a regression, even though W03 finally has an identifiable upper-right source region. Inspect the weather glow/haze and foliage transparency/depth interaction; correct the integration with the existing foliage before treating it as a reason to replace trees. A still cannot identify the precise shader or render-order cause.

4. **The two flash types still need a clearer spatial and surface response.** W03 default now brightens the upper-right road/air more than the foreground, which is the right direction. Its bright area is nonetheless a fairly flat milky wash; it does not produce the target's coherent cool distant haze and wet far-road gleam. Keep the near roof underside, lower-left foliage, and near road dark while improving the distant source falloff and selective upward-facing/wet highlights. The strong capture remains broadly gray-green and evenly lifted, particularly on bare ground; it is very similar to W01. The target is a cold broad flash with luminous upper air, bright damp edges, and substantial deep shadows. Make the strong event broader in its lighting response without turning the whole ground into a pale diffuse plate. No visible bolt is present in either submitted W03 peak frame.

5. **Rain impact integration remains conspicuous.** Thin rain strokes are visible, but the target's finer coherent rain field and wet surface response remain stronger. Isolated blue ring outlines on the ground are large and graphic relative to their surroundings. Reduce the most conspicuous ring sizes/opacity, vary them, and seat their contact appearance on existing surfaces. Improve precipitation depth and lighting response rather than flooding every depth equally. Pale blue roadside smudges are also visible in the dry grove; their source is not identifiable from stills. Check whether they are weather fixtures before suppressing anything, and preserve accepted stones/scenery.

## Per-target deductions and inherited discrepancies

### Dry prestorm forest

Both W03 grove images remain dry-looking: they lack the obvious rain streak field visible at the abbey. The character and route are readable, and overall darkness remains in roughly the same practical range as normal rain. The grove appears substantially unchanged from W01, which is why its score stays 5.20.

The target is enclosed by overlapping canopy, trunks, undergrowth, and a large foreground rock. W03 has isolated rounded tree crowns, much more open ground, and small separated rocks; `weather-104.png` is particularly open. Target foliage is muted gray-olive with deeper canopy pockets and layered haze; actual foliage is greener, and large exposed ground regions flatten the atmosphere. Weather tint/haze can improve this, but cannot manufacture the missing canopy volume.

Smooth pale trunks, repeated thin foliage cards/white branch lines, sparse wiry grass, a smoother ground base, and conspicuously repeated pale road stones remain materially different from the target's bark, leaf litter, irregular soil, moss, and small-scale surface variation. The target also includes drifting leaves. Those asset/layout differences count against composition/material/detail fidelity. They do not authorize rebuilding accepted forest, road, camera, or player within a weather pass. A dry-looking still does not prove that this section precedes rain during traversal.

### Default distant flash

Abbey-left, road-center, and trees-right remain close to the target composition. Minor camera/player framing, wall silhouette, roof structure, vegetation mass, and ground-detail differences persist. W03's upper-right light pool is a real improvement over W01's uniform lift. The source still lacks convincing air/surface depth, and the pale card-like upper-right canopy is now a material-integrity deduction.

The warm doorway lamp remains readable and the player remains identifiable. Target wet cobbles have pronounced irregular relief and localized glints; actual pale stone shapes remain comparatively flat. The target roof has coherent wet sheen and more detailed tiles, whereas the actual roof is largely matte and dark. Actual exposed ground has fine uniform sparkle rather than a varied mix of mud, wet foliage, and puddled relief. Most of these material/asset gaps are inherited. Weather reflection/light integration is in scope; a replacement road/roof/vegetation asset package is not implicitly authorized.

### Rare strong flash

The broad brightening is visibly stronger than normal rain/default across much of the image, with no visible bolt. Player, route, and abbey stay identifiable. This establishes an amplitude distinction in the supplied stills only.

The broad gray-green lift, bright foreground ground, strong greens, weak wet-edge highlights, and underdeveloped luminous upper atmosphere remain substantially the W01 appearance. The strong target retains darker foreground pockets and concentrates more brightness on wet relief and upward-facing edges. Existing low-detail/matte roof, flat road stones, sparse grass, and simple foliage limit full fidelity independently of the lighting correction. Rarity, pulse width, decay, return to normal darkness, and runtime-wide absence of bolt geometry are unproven here.

### Night blizzard

The deep-pass route and flanking rock/conifer arrangement remain a useful structural match. W03's primary capture places the player visibly higher and slightly farther right than the target and W01, with corresponding landmark shifts. Do not compensate by moving protected scenery; a later comparable capture should stabilize the player/camera framing. The approach at `weather-282.png` is a different location and is used for weather consistency rather than exact rock matching.

W03 has darker snow illumination and abundant wind-like streaks, both clear improvements over W01's bright open snow and sparse dots. The major remaining lighting and depth defects are described above. Dark trees/rock undercuts against brighter smooth snow and crisp cast shadows still produce a clear cold winter scene. The target integrates objects through diffuse light and blowing powder; adding sharp streaks has not produced that integration.

Snow caps remain thick, smooth, rounded forms with dark undercuts; the target has more irregular rock/snow interfaces and wind-eroded powder detail. The approach still exposes large dark road patches and stark wiry grass; deep snow has a more continuous cover. These are inherited snow material/mesh and transition discrepancies. They reduce the material score but are not automatic weather authorization to remodel rocks, conifers, terrain, road, or player.

The player remains easy to locate in both W03 snow frames, and the central route is still trackable. That is useful readability evidence. Fine silhouette detail is interrupted by some bright streaks, and the target's softer powder treatment would preserve a more cohesive image while obscuring the distant road more strongly. Avoid using a uniformly opaque veil that removes nearby navigation cues.

## Pro loop implication and evidence limits

The full-image gain from the supplied prior judged round is only 0.2875 points. Snow lighting and spatial flash response are repeated findings. This meets the installed Pro workflow's **stall-approaching** reason to stop small parameter-only tweaks and reassess the weather rendering approach: lighting versus surface brightness, weather depth layers, and foliage/haze integration. The judge has not been given a W02 verdict and does not assert whether a prior architectural attempt has already met the stricter **stalled** condition. The implementation owner must reconcile that with the actual iteration history. This verdict does not authorize a broader scenery redesign.

Observed in stills: dry-looking grove; rain at abbey; no visible bolt in the two supplied peak images; identifiable upper-right default illumination; broadly stronger flash; darker W03 snow than W01; dense streak appearance; readable player/route; residual bright snow/cast shadows and distant-flash foliage artifact.

Not proven: dry-before-rain order, zone transition smoothness, flash frequency/rarity/duration/fading, absence of bolts at every runtime instant, particle motion/gust coherence, audio absence, sustained performance, traversal/collision, or byte-level preservation of accepted scenery. These must come from the parent's runtime/protection evidence. Do not present this verdict as certification of any of them or as final user acceptance.

Only `Migration/Evidence/Expansion/WeatherWorld/W03/judge.md` was authored by this judge. Targets, screenshots, source code, scene assets, prior verdicts, and other evidence were preserved.
