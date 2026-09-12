# W01 independent visual verdict

Date: 2026-09-11. Reviewer: fresh Dream Loop Pro visual judge subagent. This review used direct `view_image` inspection of all four supplied target images and all seven supplied, unmodified Unity captures. No implementation code or previous score was used to infer appearance. Targets are 2688 x 1520; actual captures are 1920 x 1080. Comparison is of normalized framing and visible appearance, not an asserted pixel-perfect registration.

**Verdict: full target fidelity 5.49/10; below the Pro 8/10 visual exit threshold. The weather package needs another visual pass, principally for night blizzard and spatial flash lighting.** The absence of a visible bolt in the two flash captures and the dry-looking forest are useful visible results, but do not compensate for the target gaps. No performance, timing, audio, continuous traversal, or final user acceptance is certified by this review.

## Scores

| Target | Actual evidence | Composition /3 | Lighting /3 | Materials /3 | Details /1 | Total /10 |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 01 prestorm forest | `capture/weather-84.png`, `capture/weather-104.png` | 1.80 | 1.75 | 1.35 | 0.30 | **5.20** |
| 02 default distant flash | `capture/abbey-distant-flash.png`; baseline context `capture/weather-198.png` | 2.60 | 1.35 | 1.40 | 0.30 | **5.65** |
| 02 rare strong flash | `capture/abbey-strong-flash.png`; baseline context `capture/weather-198.png` | 2.60 | 1.65 | 1.40 | 0.30 | **5.95** |
| 03 night blizzard | `capture/weather-323.png` primary; `capture/weather-282.png` supporting approach | 2.65 | 0.65 | 1.70 | 0.15 | **5.15** |
| Equal-weight average | Four target scores | 2.4125 | 1.3500 | 1.4625 | 0.2625 | **5.4875 (5.49)** |

Scores measure the entire image against the target, including inherited scene differences. They are not a weather-only score. The following ownership distinction prevents those deductions from becoming automatic authorization to rebuild protected scenery, road, or player.

## Weather-package blockers, in priority order

1. **Snow is much too bright and clear to read as the requested night blizzard.** In both `weather-282.png` and `weather-323.png`, large snow surfaces are light, pastel blue and the scene retains strong, well-defined tree shadows. The target uses substantially darker slate-blue midtones, lower distant visibility, and diffuse storm illumination. Correct the snow area's weather lighting/exposure locally. Retain enough value separation for the player and road; do not globally darken the accepted rainy scene to solve the snow problem. Verify the change at both the approach and the deep pass, not only one chosen location.
2. **The blizzard's main visual structures are absent in the submitted frames.** Actual snow consists primarily of tiny, sparse dots with very little visible streak length. The target has many slanted streaks at several depths plus broad translucent plumes sweeping across the road and behind/in front of scene objects. Add or correct a layered wind-driven snow treatment: fine distant streaks, a denser middle layer, some longer/softer near flakes, and broad broken drifting snow veils. Give the upper/distant road noticeably stronger atmospheric loss than the near player area. Preserve the route's readability and the physical scenery. A flat uniformly dense screen of dots will not solve this gap.
3. **The default flash lacks a distinct distant source.** The supplied default frame is only a modest, rather uniform brightness lift from `weather-198.png`. The target's pale blue-white glow is concentrated at the upper-right distance, then falls off toward a much darker foreground. Add a soft, off-screen/distant illumination contribution affecting distant haze and reflecting off the far road; limit near-ground fill. This must remain illumination without any bolt geometry. The current frame does not visually establish the intended distant default flash strongly enough.
4. **The strong flash is broad, but too uniform and green/gray.** Actual ground across much of the frame becomes pale and evenly exposed while foliage stays conspicuously green. The target is a cold broad flash with bright wet edges, lifted upper haze, and retained deep foreground shadows. Shape the flash with directional/sky illumination and atmospheric scattering so it has depth and surface response, not only an ambient/exposure lift. Preserve the useful stronger-versus-default brightness distinction already visible in these two images. Do not turn the rare strong peak into a sustained daytime look.
5. **Weather detail integration needs restraint and depth.** Rain streaks are visible, but the target has a denser, more cohesive fine rain field and wet surface response. Several actual splash rings are isolated, large, bright blue circles that read as effect sprites against relatively flat ground. Reduce conspicuous ring outlines/size, vary their opacity and scale, and visually seat impacts on surfaces. Improve the distance/foreground hierarchy of precipitation rather than increasing every particle equally.

## Target-specific observations and deductions

### 01: dry dark forest before rain

- **Visible success:** neither dry-forest capture shows the obvious rain streak field found in the abbey captures. The route and character remain legible. The overall state reads as subdued overcast woodland, and the road does not have the target rainy area's extensive wet gleam. Static evidence supports a dry-looking segment, not the chronological order of weather transitions.
- **Composition:** the target encloses the road with overlapping large canopies, trunks, undergrowth, and a prominent foreground rock. Actual `weather-84.png` is appreciably more open; `weather-104.png` exposes especially large empty ground areas. Small isolated stones and evenly separated rounded tree crowns replace the target's layered forest wall. The character also occupies somewhat more of the forest frame than in the target. These differences materially reduce full-image fidelity.
- **Lighting:** the target has more muted gray-olive foliage, deeper canopy pockets, softer layered haze, and a browner road. Actual leaves remain more saturated green and the broadly exposed ground gives a flatter, less enclosed atmosphere. A restrained local weather tint/desaturation and depth haze could help, but dimming alone cannot manufacture the missing canopy mass. The current dry darkness is broadly in the neighborhood of the supplied normal-rain capture; preserve that practical anchor.
- **Materials:** actual trunks look like smooth pale cylinders, tree crowns expose repeated thin cards and white branch lines, grass is sparse and wiry, and the road stones form a conspicuous repeated pale pattern on a relatively smooth base. Target trunks, mossy rocks, leaf litter, soil, and road have much finer variation and irregularity. These are scene/asset differences, not evidence of failed weather code.
- **Details:** the target includes small drifting leaves and richer ground litter. Actual road shoulders also contain a few pale blue flecks/smudges. Their source is not identifiable from the screenshots; if they are rain splash/foam fixtures, suppress those fixtures in the dry section. Do not remove real stones or accepted scene features based only on that possibility.
- **Scope classification:** color/atmosphere and any confirmed residual rain effects are weather-package work. Tree model replacement, dense new planting, rock relocation, road retexturing, camera alteration, and player changes are inherited/scene-level fidelity gaps that require a separate scope decision. The review does not authorize them.

### 02: default distant flash

- **Composition:** the abbey-left / road-center / trees-right arrangement is close to the target. Minor differences remain in camera alignment, the character's vertical framing, ruined wall silhouette, roof detail, and vegetation mass. They are not reasons to move the accepted road or rebuild the abbey during weather correction.
- **Lighting:** target far road and upper-right air are conspicuously illuminated while the roof underside, near roadside, and lower-left foliage stay dark. Actual default illumination is flatter, with no convincing bright distant atmospheric pool. The warm doorway lamp survives, but target cool/warm separation is stronger.
- **Materials:** the target cobbles and roof have visible wet highlights, small relief, and varied reflection intensity. Actual road has comparatively flat pale stone shapes, the roof looks mostly opaque/matte, and the exposed ground shows broad fine sparkling texture rather than convincing mixed mud and wet vegetation. Prioritize weather light/reflection integration with existing materials; replacement textures/meshes are inherited scope.
- **Details:** there is no visible lightning bolt in the submitted frame. Rain and isolated impact circles are present, but their density, scale, and integration differ from the target. The absence of a bolt in one image is not proof that no bolt appears anywhere in the runtime.

### 02: rare stronger broad flash

- **Composition/material inheritance:** the same abbey differences apply as above and are scored consistently.
- **Lighting:** the strong capture is clearly brighter than the distant capture; it therefore shows a meaningful amplitude distinction in still images. It also illuminates a broad area without an obvious bolt. However, its broad brightening is overly even, and the foreground ground rises too much relative to the roof/foliage. Target brightness is more concentrated on damp, upward-facing edges and distant air; the actual result reads more like a brighter lighting preset.
- **Palette:** target flash is cold white-blue with deep dark foliage retained. Actual greens remain strongly visible and the terrain becomes milky gray-green. Correct the weather light color and spatial response before touching accepted asset albedos.
- **Details:** target rain is brighter and more coherent during the peak, with subtle local wet glints. Actual flash does not reveal the same surface microstructure. Do not compensate using a featureless white overlay that erases the player and route.
- **Unproven:** rarity, pulse duration, fade shape, multiple pulses, and preservation of normal darkness between events cannot be judged from these two isolated peak captures.

### 03: night blizzard

- **Composition:** `weather-323.png` already has a close overall route / left rock mass / right rock mass / snow-covered conifer arrangement. The straight road and centered player provide a solid foundation. `weather-282.png` is a different approach location, so it is used for weather consistency, not exact rock-position matching.
- **Lighting blocker:** the bright blue ground is the dominant mismatch. Although the trees are dark, the scene as a whole reads as clear blue winter daylight/twilight. Deep-night atmosphere cannot be inferred from the zone label. The target is darker, more muted, and much more obscured by blowing snow.
- **Materials:** actual snow on rocks has smooth, thick, rounded frosting-like caps with hard dark undercuts; target snow/rock edges are more irregular and subtly textured. Target ground has wind-eroded powder variation and softer route blending. Actual `weather-282.png` has notably exposed dark road patches and stark wiry grass, while the deeper `weather-323.png` route is more uniformly covered. These existing snow mesh/material and transition details reduce fidelity independently of the weather effect.
- **Details blocker:** the target's dominant slanted snow streaks and layered white plumes are missing from the visible result. Actual air is mostly clear, making distant rocks, trees, and route almost as sharp as foreground elements. Fix weather depth and particle presentation before considering any snow mesh changes.
- **Do not change to solve weather:** player, route alignment, conifer placement, and rock formation geometry. These already support the target well enough for a weather-focused pass.

## Scope and verification limits

- **Observed only:** dry-looking forest frames; rain in the abbey; no visible bolt in the two flash frames; strong capture brighter than default; snow-coated scenery with sparse visible flakes.
- **Not demonstrated by stills:** dry-before-rain ordering; smooth world transitions; default/rare frequency; event duration and fading; particle motion and wind coherence; thunder/other audio absence; runtime never showing a bolt; player traversal; frame rate; preservation relative to an earlier accepted build. Verify these separately with runtime evidence and the applicable protection audit.
- **Inherited target discrepancies:** vegetation density/model quality, bark, grass, road and wet material fidelity, ruined-building detail, snow-cap shape, some framing and small layout differences. They contribute honestly to the scores but do not authorize changes to protected scenery. There is no separate inflated weather-only pass score.
- **Next review:** submit the same dry, normal rain, distant flash, strong flash, snow approach, and deep snow viewpoints after weather changes. In addition, retain a short continuous capture across normal light -> default flash -> normal light and a separately identified strong event, plus a snow traversal clip. Timing/audio/performance conclusions must come from those appropriate checks, not from this screenshot verdict.

Only this verdict file was authored by the judge. All images, source, scene assets, and existing evidence were preserved.
