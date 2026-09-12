# Latest decision: user accepts candidate58 quality

On2026-09-09 the user accepted the delivered candidate58 quality as sufficient. This supersedes pending-user-adoption wording below without changing the original visual observations, independent candidate52 score or player measurements. Further old-target visual iteration is closed. The [reviewed expansion plan](../../../EXPANSION_PLAN.md) is documented but not implemented. New character/environment acceptance remains separate from this baseline decision.

# Previous: candidate58 playable handoff

User requested finishing for play. Saved scene58 and Windows player are delivered; see candidate-58/SELF_REVIEW.md and player-58/VALIDATION.md. New build0errors/0warnings; static 43.45, walk 44.09, orbit 43.44, zoom 43.84 FPS. Original visual8/10 and60FPS remain unmet. Latest independent score belongs to52 (6.1/Tier2). No58 score or final adoption. PLAY_VESPER.cmd launches interactive mode. The following records are historical.

# Atmosphere restoration work log ? 2026-09-08

## Latest candidate41, 2026-09-09

See `candidate-41/SELF_REVIEW.md` for the direct four-view surface audit and
`verdict-unity-7.md` for the independent6.0/Tier2 judgment. The combined asset
strategy changed wood, photographic paving and stair construction. The judge
confirmed the wood's substantial progress but found the floor too shallow and
the masonry bands still dominant; some clean portal blocks regressed locally.
Preserve the useful irregularity and restore visible slab relief, pools, broad
edge fractures and root contacts. Do not treat the new asset labels or clean
player build as visual acceptance. Player41 cadence/motion checks are pending.

## Previous resumed candidate36, 2026-09-09

Current saved scene and final TreeV10/PavingV10 source are synchronized in36.
All four actual Unity views were inspected against the original concept and30.
The new independent judge scored5.8/Tier2 (`verdict-unity-6.md`), following30's5.6.
Connected curved wood, broad roots, worn stone outlines and dielectric water are
structural improvements, but the visible paving grid became cleaner and more
regular, so its geometric treatment is still insufficient. The weak left fire
reflection, tile-local wet gloss, banded stair/pier construction and broad tubular
limbs remain. No visual completion is claimed. The next pass changes asset
strategy with photographic paving, generated detailed wood and integrated stair
stones; small parameter changes cannot clear Tier3.

Candidate36 player build:0errors/0warnings. Clean frame cadence58.75–59.93FPS,
all focused, zero runtime errors, no concurrent Unity/Blender render. This is near
60 natural-loop cadence, not measured display-present FPS. Automatic motion
recording separately moved13.478m and recorded318 frames at10.02–10.94Hz. Original
upright images0000,0033,0098,0194,0256,0317 directly inspected: walking turn changes
are visible; orbit/zoom preserve surfaces; zoom boundaries no longer expose the
old backdrop rectangle. Wide/low views expose repeated facades and simplified
depth, and close/high views emphasize the material grid. The video preserves
actual frame timestamps. Windows native input is still unavailable despite user
authorization; no latest direct-input pass is claimed.

## Candidate28 safe-stop self-review

Candidate28 integrates KnightV5 and replaces the separate standing-water shader's wide vertical multi-sample blur with a tight three-tap reflection. The photographic stone path no longer multiplies the albedo by2.5 into clipped gray; dry normal/roughness contrast is stronger and the separate-water floor no longer receives the same near-mirror wet smoothness. DepthNormals now initializes `normalTS` explicitly.

I directly inspected full/orbit/zoom/slice against the concept, browser baseline and candidates23/26/27. The white cloud-like water smears are substantially reduced, warm reflection shapes are more localized, and KnightV5's softer folds and uneven hem remain visible in Unity. The result is still not judge-ready: dark reflected regions form broad blotches, Rock01 mineral relief remains too weak at full-frame distance, and the known portal/stair repetition and tree silhouette gaps remain. No independent score was requested, and the last independent Unity score remains candidate23 at5.4/Tier2.

Technical evidence `candidate-28/capture.json`: shader errors0, runtime errors0, missing scripts0, reflection updates120 on Intel Arc130V. No player build, FPS benchmark, direct input or continuous motion review was run before the user-requested safe stop. This is a saved diagnostic candidate, not visual completion or adoption.

Original browser/Unity slice images (1037x739), target and browser full image (1536x1024) were directly inspected. Original assets, scene, settings and past evidence are preserved. New candidate is VesperAtmosphereV2; no independent Unity score assigned yet.

## Diagnostic passes, not judge rounds
- Pass 1: additive versioned materials, mist layers, rune lights/lines, cinders, wet reflection energy and firelight distribution. Self-review: floor still lifted/chalky, backdrop too uniform. Three capture target-release lifecycle errors; subsequently fixed by detaching camera before release. Not judge-ready.
- Pass 2: local stone energy and fog isolation, correct rune height. Self-review: still missing projected flame shape and pooled-water contrast. Not judge-ready.
- Pass 3 / fresh process: camera-aware fire billboarding for reflection pass, separate runtime orbit camera and saved candidate. Zero shader/runtime/missing-script errors. Self-review: reflection buffer improved but surface projection remains suspect. Not judge-ready.
- Pass 4: generated stratified stone surface, spatial detail normal, restored cloudy environment reflection, compressed pauldrons. Zero shader/runtime errors. Self-review: source target still materially ahead; reflection buffer contains a full flame, but floor shows mainly point-light highlight. Investigating texture-coordinate convention before any judge submission.

No visual completion or FPS acceptance claimed from these captures. Actual player build and direct input review follow the prepared visual candidate. Browser score 6.5 is historical browser-only.

## First independent Unity submission
Prepared candidate: round-7/full.png, 1536x1024. Recovery fresh-process screenshot is visually equivalent (mean channel delta below 0.12/255, animated effects not frozen bit-exactly), with zero shader/runtime/missing-script errors.

Self-review, surface by surface: major tree/knight/stairs/portal composition is present; real reflected flame now projects to the floor after D3D UV origin correction, warm spill and rune/embers are present; blue background is layered with moving mist. Material energy, custom detail map, reflection and billboarding have been changed in the implementation rather than screenshot retouching. Native candidate has substantially more complete visual behavior than the initial migration. It is ready for a first independent native score to guide the remaining target work, not a claim of target completion.

Known limitations: flat repetitive paving and stair faces, insufficient pooled water, thin twig shapes, facade bottom terminations, cape drape and narrow fire reflection still differ from the target. The first player run is around39 FPS at1536x1024, zero runtime errors, valid click/wheel/reset; injected short drag did not register as a drag. These are open implementation/performance issues. No inherited browser score is assigned to Unity.

## Candidate for independent Unity review 2
- Native screenshot: round-13-water-brdf/full.png, 1536x1024; same target framing as prior round-7.
- Structural work since review 1: 36 combined batches replaced from ten Blender stone variants; tighter mortar gaps; seven Blender knight mesh replacements; native water-film BRDF with separate directional/point-light response; actual projected reflection retained. Foreground water still needs broader fragmented pools.
- Atmosphere diagnosis: no-mist render proved the large left veil was overlapping mist planes. Reducing them exposed layered castle silhouettes. Base mist still needs better integration with long lower supports.
- Full/orbit/zoom inspected directly. Round-11's silver orbit wash was rejected and corrected in the lighting implementation. Round-12 initially had one overload compile error and magenta render; retained as failed evidence. round-12-fixed and round-13 have zero shader/runtime/missing-script errors.
- Self-review: composition intact; shoulder balls removed and cape folds improved; connected floor faces read more convincingly than prior rounded separated tiles; gold stair highlights exist and broad warm wash reduced; castle detail visible through mist. These are meaningful improvements across the prior blockers and support a fresh score.
- Not target-complete: too few pooled reflections, stair/portal repetition, tree angularity and thin spikes, visible foundation terminations, subdued cool foreground highlights, flame hardness remain. Motion/FPS validation still required for this candidate. Do not copy browser 6.5 or call the technical pass a visual pass.

## Candidate18 fresh independent submission self-review
Native full1536x1024 directly opened alongside original target and earlier candidates. Major structural change after the two low-scoring reviews: voxel-joined treeV8 (51,654 triangles), restored distal root tips, replacement curved split twigs; mineral albedo now comes primarily from generated stone texture and legacy long normal grooves are reduced; separate directional/point water-film response and restrained point flame core; height fade removes hard lower support terminations; backgroundright attenuation and cool direct/fill rebalance. Native full view is materially more readable and detailed than candidate13, with stronger root continuity, mineral faces and reduced saturated flame area. This warrants a fresh independent assessment of the remaining gates.
Remaining defects: large repeated portal/stair shapes, water reflection footprint still too concentrated, cool wet patches weak at target camera, some twig spikes and bark noise remain; full atmospheric fidelity not accepted. Candidate15 oval pool geometry remains excluded. Candidate18 haszero shader/runtime/missing errors. Player16 confirms fixed pointer input but its FPS was contaminated by Blender, so a fresh candidate18 player test follows with all other render jobs stopped.

## Structural passes19?23, not independent judge rounds

- Fresh judge3 on candidate18:4.9/10,Tier1. The remaining repeated wet-light distribution failure triggered a structural strategy change, not score inheritance from the browser.
- Candidate19: authored irregular wet-mask and flattened water normals removed the orbit sparkle carpet, but warm reflections missed parts of the mask and sky reflection was absent in the planar background. Not judge-ready.
- Candidate20: actual cubemap sky rendered by the planar camera established five bounded pool regions. First sky energy was grossly too bright/blue; this diagnostic is preserved and not adopted.
- Candidate21/22: separated warm/cool reflection response, mask placement corrected for projected flame positions, dark vessel material, reduced portal/brazier spill, selective background softening, per-instance mineral rotation, legacy long normal grooves nearly removed.22 restored quieter cool pool regions but direct shadows remained too subdued.
- Shadow diagnostic: actual main-light shadow attenuation directly rendered for all masonry. Tree and knight shadows are present; reflection rendering is not deleting them. Excess baked ambient fill relative to direct moon energy suppresses their final contrast. A no-reflection diagnostic captured its slice then failed on a null reflection buffer; the optional capture path was fixed and the failure retained.
- Candidate23 integrates StoneV7 runtime derivative (8,770 total unique triangles,+24.86% overV6; exactbounds/closedness/normals checked in Blender), lowers ambient fill and increases direct moon contribution, and enables soft shadows. The render is reviewed before any new judge submission.

Clean player18 benchmark, with Unity/Blender stopped: static51.74,walk52.14,orbit51.58,zoom52.95 FPS;1536x1024,allframesfocused,zero runtime errors. The walk segment includes resting after a2.44m traversal. This is natural player cadence, not hardware display-present tracing, and is below60FPS. Priorplayer16 direct input verification remains separate.

## Candidate23 prepared for independent review4

Direct full and orbit1536x1024 review against concept and candidate18: five bounded irregular cool water regions now coexist with dark stone; dense white orbit sparkle carpet removed; actual sky and fire rendered into planar reflection; warm/cool reflection energy separated; legacy long normal response nearly removed and mineral sampling rotated per instance; vessel tops no longer broad yellow areas; nearest right panorama selectively softened/desaturated toward cyan; tree/knight cast shadows now clearly read after reducing fill relative to moon. StoneV7 runtime contours retain layout and add local wear. These resolve several heavy directives structurally and support a fresh review.

Still open: main warm reflection narrow compared with target; some water areas read as rough patches rather than continuous shallow water, repeated portal/stair courses, tiny branch spikes, cape/character detail, and whole-reference atmosphere difference. No target-completion claim. First23 compile failed because URP supportsSoftShadows has an internal setter; fixed using its inspected SerializedObject field.23-fixed haszero shader/runtime/missing-script errors and113 reflection updates. No screenshot retouching.


## Candidates 24-27, structural surface work (not final acceptance)

- 24 separates standing water into one physically flat plane at y=-0.004, above the measured floor tops (-0.0564 to -0.0091). Its authored footprint crosses tile joints. 25 reduces excessive reflection blur. Water is continuous but the cloud reflection still appears cloudy and the warm highlight remains too soft.
- 25 installs TreeV9: 639 bark plates, four buttress roots and eight curved split offshoots; 74,671 triangles. The native render shows more trunk relief, but thin angular twigs remain.
- 26 installs six unequal masonry variants and two short facade course variants. 1,739 courses replace tall unbroken facade extrusions, with below-floor pieces below y=-12 omitted because the shader fully hides them. One third of selected floor slabs and inset lines gain alignment/size breaks. Full/orbit/zoom capture has zero shader/runtime/missing-script errors.
- 27 replaces color-derived relief with separate photographic albedo, GL normal and linear roughness maps (Poly Haven Rock 01, Rob Tuytel, CC0). Forward and DepthNormals now share the same normal function. The actual render became too smooth; this is a technically valid diagnostic candidate, not a visual adoption. A more strongly eroded source is being compared next.
- No new independent score is assigned to 24-27. Latest independent result remains candidate23 5.4, Tier2. These candidates are not claimed >=8 or 60 FPS.


## Safe stop requested by the user

Stopped without further visual iterations. The saved scene is candidate27, a diagnostic whose photographed stone looks too smooth; it is not visually adopted. A fresh Editor capture after disabling FrameTiming via Editor API passed zero shader/runtime/missing-script errors,108 reflection updates, and the full image was inspected. KnightV5 was inspected in Blender and preserved under tracked Source, but not integrated.

Instrumented Windows player27 built with0 errors/5 warnings and ran with0 runtime errors. It reported29.0-32.1FPS,31-35ms median GPU time, all frames focused. The UI capture did not establish the game image, so an earlier suggestion that the benchmark was occluded is not treated as fact. This is not a matched noninstrumented comparison with player23, not direct input verification and not hardware display-present timing. Performance remains below target and the cause is unresolved. Two D3D11 potential normal initialization warnings and the inherited flame pow warning remain recorded for the next code review.

Latest independent score stays5.4/Tier2 for candidate23. No judge-ready claim is made for27. All current Unity/Blender/player processes exited; all delegated jobs completed. CHECKPOINT records the precise resume state.
