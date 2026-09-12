# Material textures V2

Two new original Higgsfield Nano Banana Pro 2K material albedos, generated through the explicitly requested installed CLI. All prior textures, scenes and builds are preserved. No input image uploads, procedural image edits, normal maps, paid top-ups or subscriptions were used.

| Original | Purpose | Job | Charge |
|---|---|---|---:|
| PackedAlpineSnow.png | Localized packed/compacted route snow; irregular crushed grains and pale icy gray-blue compression, no recognizable footprints or tracks | d687ef50-6053-491e-aa08-b1f3311bbbb0 | 2 |
| WetAbbeyLimestone.png | Rain-saturated blue-gray abbey stone color, tiny pits, worn grains and restrained fractures; no slab grid, puddles or specular reflections | 7919d6e6-4163-4598-af27-7622d9839b90 | 2 |

Both images are original2048×2048 opaque RGBA PNGs, downloaded without resampling or modification. Use as sRGB base color, repeat wrap, full0..1 UV rather than atlas-quadrant ST. Prompted approximate source scales are2m square for snow and1m square for stone; parent owns material scale, wetness, terrain blending and Unity acceptance.

Snow has materially stronger microgranular contrast than the old smooth SnowSurface: sampled adjacent-pixel luminance RMS is8.15 versus1.55 (5.25×). It includes some larger angular snow clods and should be used selectively on packed areas. The new limestone is cooler and darker than the old cream-gray map. A repeated half-frame stone motif is perceptible in the generated original; existing per-slab rotation/UV offsets can reduce repetition. No visible tile-grid borders or strong directional cast shadows were observed. Prompted seamless tiling is not a mathematical guarantee; boundary statistics and runtime repeat-mode inspection remain separate evidence.

`*-prompt.txt` preserve the full exact prompts. `*-job.json` preserve the final original job metadata. `submission-provenance.json` records sequentially queried latest ledger charges and balances; `texture-delivery.json` contains download hashes/dimensions. `texture-pixel-audit.json` records read-only edge, color and microcontrast measurements; no images were changed by measurement.

The CLI creation response was a list of job-ID strings. The two existing submitted jobs were recovered by exact full-prompt matching when the initial response parser expected objects; no duplicate generation was made. Exact added ledger cost is4 credits, balance2,440→2,436, active-run total90 (prior86+4). Job linkage uses the latest ledger transaction queried after each separate job, with matching timestamp/model; the ledger has no direct job-ID field.

`staged/` is the frozen Art batch: two originals plus manifest/provenance JSON. Intended destination is `Unity/Vesper/Assets/Vesper/Expansion/ContinuousWorld/Art/Textures/MaterialTexturesV2`. Parent explicitly reviewed both originals and opened the import window before copying. Old texture files remain untouched.
