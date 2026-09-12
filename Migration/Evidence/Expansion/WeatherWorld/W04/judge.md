# W04 independent visual verdict

Date: 2026-09-11. Reviewer: fresh Dream Loop Pro visual judge subagent. Review was read-only except this verdict. The installed `dream-loop/SKILL.md` and linked Pro workflow were read. All four targets, all seven requested W04 raw Unity captures, and all seven corresponding W03 captures were inspected directly with `view_image`. W03 and W01 verdicts were read for scoring continuity. No implementation code or numeric image statistics were used to infer appearance.

The four targets are `.dream-loop/weather-world/targets/01-prestorm-forest.png`, `02-default-distant-flash.png`, `02-rare-strong-flash.png`, and `03-night-blizzard.png`. Targets are 2688 x 1520 and were displayed at 2048 x 1158; submitted Unity captures are 1920 x 1080. Comparison uses proportional framing, without claiming pixel registration. Five additional W04 snow motion frames were inspected, as identified below.

**Full target fidelity: 5.9125/10, displayed as 5.91/10. W03: 5.7750/10 (5.78). Gain: 0.1375 points. W04 is below the Pro 8/10 visual threshold.** The default-flash foliage correction and softer snow shadows are visible improvements. The strong flash remains insufficiently integrated with wet surfaces. Snowflakes look less artificial individually but the visible storm is substantially weaker than W03 and still far from the target blizzard.

These are full-image fidelity scores, including inherited scenery/material differences. They are not a weather-only acceptance score. Meaningful visible fixes exist, but they do not establish full target completion, runtime quality, or final user acceptance.

## Scores

| Target | W04 evidence | Composition /3 | Lighting /3 | Materials /3 | Details /1 | Total /10 | W03 total |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 01 prestorm forest | `capture/weather-84.png`, `capture/weather-104.png` | 1.80 | 1.75 | 1.35 | 0.30 | **5.20** | 5.20 |
| 02 default distant flash | `capture/abbey-distant-flash.png`; `capture/weather-198.png` context | 2.60 | 1.85 | 1.40 | 0.30 | **6.15** | 5.90 |
| 02 rare strong flash | `capture/abbey-strong-flash.png`; `capture/weather-198.png` context | 2.60 | 1.65 | 1.40 | 0.30 | **5.95** | 5.95 |
| 03 night blizzard | `capture/weather-323.png` primary; `capture/weather-282.png` supporting approach | 2.65 | 1.75 | 1.70 | 0.25 | **6.35** | 6.05 |
| Equal-weight average | Four target totals | 2.4125 | 1.7500 | 1.4625 | 0.2875 | **5.9125 (5.91)** | **5.7750 (5.78)** |

The default-flash material score recovers the W03 deduction for washed-out foliage. Lighting gains a small amount for the cooler, better-separated distant treatment. The strong-flash lighting score stays unchanged: the colder palette improves target direction, but broad pale ground and insufficient highlight/shadow selectivity offset it. Snow gains for softer lighting and more comparable framing, but loses detail credit because target-like storm coverage is weaker. The snow material score is unchanged; softer illumination does not establish improved snow geometry or texture.

## Remaining weather blockers and regressions

1. **The blizzard is now visually too sparse.** W03 had conspicuous hard, nearly horizontal slashes; W04 replaces them with much smaller, mostly diagonal marks that look more like individual flakes. That is a shape improvement. However, the marks occupy far less of the image, leaving wide clear air between them. In both W04 snow locations, the result reads as light snowfall over a cold landscape rather than the target's dense wind-driven storm. This is a regression in storm strength, not a reason to restore the previous hard streak field. Retain the softer diagonal vocabulary while establishing a much more visible depth hierarchy: fine distant snow, varied middle streaks, and a limited number of larger soft near flakes. Judge that hierarchy at ordinary FHD viewing size, where the current flakes nearly disappear against the snow.

2. **Broad blowing powder and distance loss remain weak.** Soft low wisps are visible around the player/lower road in W04, so it would be inaccurate to call every powder contribution absent. Nevertheless, the target's broken translucent plumes cross large portions of the route and overlap rocks/trees at different depths. W04's distant road and canopy boundaries remain comparatively clear. The atmosphere is largely a blue ground gradient with small particles above it. Establish irregular powder volumes that obscure different depths and break up the upper road without erasing the nearby route. A uniformly opaque full-screen veil would lose the useful player/road readability that W04 retains.

3. **Night illumination improved but still lacks the target's integrated storm atmosphere.** W04 reduces the sharply recognizable tree shadows and the long conspicuous player shadow seen in W03. This is a real visual gain. Broad snow planes remain comparatively bright and smooth, while conifers and rock undercuts stay nearly black. The target has darker slate-blue midtones, less stark object/ground separation, and stronger atmospheric integration. The approach at `weather-282.png` is particularly open and clear. Continue to distinguish ambient/object fill from snow-surface brightness; simply darkening everything would push already-dark trees/player farther into cutouts. Keep normal-rain darkness as the existing anchor rather than lowering the entire world.

4. **The distant-flash foliage regression is corrected, but the light still reads too much as a ground wash.** W04's large upper-right trees preserve a dark green canopy mass instead of W03's pale/translucent leaf planes and dark skeletal branches. That specific defect is no longer a blocker in this peak frame. The upper-right far road is clearly brighter than the near roof underside. However, the glow continues across road, bare ground, and ruin interior as a broad milky fill, with sharply outlined thin grass above it. The target has luminous distant air and coherent wet far-road gleam. Keep the canopy fix and distant emphasis; improve light response on existing wet upward-facing surfaces and retain darker near-road/near-ground pockets. Do not solve this by making all distant foliage pale again.

5. **The strong flash is colder, but its selective surface response is not convincingly improved in the pixels.** Compared with W03, W04 ground becomes bluer, and wall tops/edges are more distinctly lit. The broad stronger-than-default amplitude remains clear. Much of the lower-left ground and route shoulder also rises into a pale diffuse plate, while the roof remains predominantly dark/matte and foliage stays conspicuously green. Existing cobbles become brighter shapes rather than acquiring the target's irregular localized wet glints. The strong target preserves deep foreground pockets and concentrates more brightness on damp relief and upper atmosphere. Reduce diffuse near-ground fill relative to wet-edge/upward-surface highlights; preserve the stronger event's broad reach without turning it into a broadly bright lighting preset. No visible bolt appears in either supplied W04 peak image.

6. **Rain/contact detail remains graphic.** Rain lines are visible, but isolated blue ring outlines remain conspicuous in the normal-rain frame, especially on the road and bare ground. The target's fine rain field and subtle impacts are more cohesive. Smaller/softer and less uniformly outlined impacts would better fit the existing surface scale. Pale blue roadside smudges also persist in both dry-grove frames. Their source cannot be identified from these images; verify whether they are weather fixtures before removing anything. They could be accepted scenery and should not be deleted based on appearance alone.

## Per-target deductions and inherited scope

### Dry prestorm forest

The grove remains dry-looking and subdued. Neither capture shows the obvious abbey rain field. The player and road are easy to locate, and general darkness is still in roughly the same practical range as normal rain. There is no substantial W04 improvement or regression against W03 in this target; the score remains 5.20.

The target encloses the road with overlapping canopy, trunks, undergrowth, and a large foreground rock. W04 has separated rounded crowns, more exposed ground, small isolated rocks, and especially open space in `weather-104.png`. Actual greens are stronger and canopy depth/haze weaker. Weather tint and atmosphere can address part of the mood difference; they cannot supply missing canopy mass.

Smooth pale trunks/white branch lines, visibly repeated leaf-card structures, sparse wiry grass, a smooth ground base, and repeated pale road stones differ from the target's bark, soil/litter, moss, and irregular road detail. Tiny warm flecks are visible in W04, but the target's leaf/litter richness is not established. These are largely inherited asset/layout/material gaps. The verdict does not authorize tree replacement, planting changes, rock moves, road retexturing, camera redesign, or player edits.

### Default distant flash

The abbey-left, road-center, trees-right composition remains close. Minor player/camera alignment and the ruin, roof, wall, vegetation, and ground-detail differences remain inherited. The warm doorway lamp survives the cool flash, and the player remains identifiable.

The recovered upper-right canopy integrity receives explicit credit. The existing foliage still has simple card-like construction and pale branches, but the severe W03 washed-out appearance is no longer present. Actual roof tiles remain smoother/more matte and road stones flatter than the target. Weather light can improve existing material response; replacing roof, road, or vegetation assets is a separate scope decision. The target's rain density, far-road relief, and wet reflections remain substantially stronger.

### Rare strong flash

The same composition and inherited material differences apply as for the default target. Broad stronger illumination and a cooler palette are visible. Player, route, and warm doorway remain identifiable. The cold shift is useful, but broad pale diffuse ground still dominates the difference from the target. This is why a stated surface-specific implementation change is not awarded additional material points.

Frequency, rarity, pulse width, return to normal darkness, and absence of bolt geometry at every runtime instant are not certified by the isolated peak frame.

### Night blizzard

W04's primary player position is closer to the target's central framing than W03's higher/right placement; composition returns to 2.65. The road and flanking conifer/rock arrangement provide a useful structural match. This framing improvement is a capture observation, not evidence of authorized scenery movement or byte-level preservation. The approach is a different location and only supports weather consistency.

Softer shadows improve lighting. The player's lower legs are lightly veiled in several samples but the silhouette and route remain readable. The main remaining weather failure is storm presence and depth, described above. W04 has not reached the target's diffuse night-blizzard appearance.

Thick smooth snow caps, rounded snow/rock interfaces, dark undercuts, sparse branch clumps, smooth ground, and the approach's exposed dark road patches/wiry grass remain inherited differences. They reduce full fidelity but do not authorize remodeling snow, conifers, terrain, rocks, road, or player. Surface and silhouette texture do not become target-matched merely because particles pass over them.

## Supplemental sampled motion evidence

Read `W04/motion/frames.csv` and directly inspected `motion-0108.png`, `motion-0109.png`, `motion-0110.png`, `motion-0130.png`, and `motion-0145.png`. The first three are consecutive captured samples at reported times 31.04859, 31.17120, and 31.30452; later samples are 33.83009 and 35.74165. They show changing flake positions and low soft wisps, while the generally sparse storm appearance persists. This reduces the likelihood that `capture/weather-323.png` alone happened to show an unrepresentative empty instant. It does not prove every gust over a complete cycle.

These images were inspected as an ordered sample set, not played as continuous video. The CSV was used to identify samples, not to infer visual success or frame rate. No claim is made about smoothness, physical particle speed, natural event frequency, flash timing, audio, display-present FPS, or continuous traversal. The parent owns those runtime checks separately.

## Pro loop implication and review status

W04's architectural attempt has visible local benefits, and the total score rises slightly. Therefore this verdict does **not** assert the literal Pro **stalled** condition of an architectural attempt followed by the same or a worse total score. The remaining blizzard/depth and flash-surface findings are still repeated gaps, and the overall gain is far below one point. The architectural change has not produced a dramatic target-fidelity advance or an 8/10 visual pass.

The user's requested stopping condition around meaningful visible changes must be reconciled by the parent with the authorized package and remaining runtime checks. It can support presenting W04 for direct review with these limitations. It must not be relabeled as full target acceptance, nor used to expand work automatically into protected scenery redesign.

Observed: dry-looking grove; rain at abbey; corrected distant-flash canopy washout; upper-right default emphasis; cooler broader strong flash without a visible bolt in the submitted peaks; softer snow shadows; finer diagonal snow; weaker apparent storm density; readable player/route.

Not certified: chronological dry-before-rain traversal, smooth transitions, event rarity/duration/decay, all-runtime bolt absence, gust motion quality, audio absence, performance, collision/traversal, accepted-file preservation, or final user acceptance.

Only `Migration/Evidence/Expansion/WeatherWorld/W04/judge.md` was authored by this judge. Images, implementation, prior verdicts, targets, scene assets, and other evidence were preserved.
