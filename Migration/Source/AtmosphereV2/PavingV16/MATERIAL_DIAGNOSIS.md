# Paving material frequency diagnosis — read-only analysis

2026-09-09. Scope: source analysis, direct candidate-52 full/zoom image inspection, direct Tiles130/Rock05 map inspection, and small CPU image statistics. No shader, imported texture, source map, mesh, or Unity scene was changed. PavingV16 structural prototype remains a separate native-review candidate. This diagnosis does not claim a proven native improvement.

## Findings

Candidate-52 full and zoom show broad, low-contrast gray slab tops. The photographed joints remain clear, but interiors do not provide the finer aggregate breakup visible in the concept. Current material has a frequency gap: Tiles130 was enlarged with the slab layout, while the added Rock05 maps are so small in world space that most mineral detail is averaged away before shading. There is no Rock05 diffuse contribution to recover diffuse-light surface variation.

Relevant source pointers, at inspection time:

- `Unity/Vesper/Assets/Vesper/Shaders/AtmosphereStone.shader:204–237`: authored Tiles130 normal uses `_BumpScale * .40`; `_SEPARATE_WATER` sets local normal-function wet to zero, so the effective macro gain is .40 with material bump 1. Rock05 micro UV is `p.xz * 3.0`, and its normal gain is 1.05. This is a 0.333m tile, not normal strength 3.0.
- Shader lines 288–305: authored `detailUV = input.uv`; diffuse is Tiles130 only. Its 82% desaturation removes chroma, but does not itself erase luminance detail. Base color and wet multiplication reduce absolute contrast. No `_MicroAlbedo` exists in this version.
- Shader lines 324–329: roughness uses the same `worldXZ * 3.0`; `mineralVariation = clamp((rough-.515)*1.7,-.15,.15)`; wet smoothness is `clamp(.58-mineralVariation,.43,.73)`. The nominal range is wider than the screen-filtered map actually exercises.
- `Unity/Vesper/Assets/Vesper/Editor/VesperAtmosphereBuild.cs:267–280`: Tiles130 color/normal/roughness/AO are attached to authored UV; Rock05 normal and roughness are attached as micro maps. Macro bump is 1, patina strength is 0, and separate water is enabled.
- Build source line 301 `ImportMeasuredTexture`: default maximum size is 4096, Repeat, anisotropy 8, uncompressed, normal/data color spaces explicitly selected. Imported Rock05 is source 2048 square with mips. Tiles meta has a legacy 2048 top-level entry, but default-platform maximum is 4096 and the Standalone 2048 block is not overridden. This is not evidence of an active 2K cap; runtime `Texture.width/height` can settle the actual import dimensions.

Tiles130 source is 4096×2048 and nominally 2.3×1.15m; the current registered period is 12.4×6.2m, an explicit 5.3913× art enlargement. It retains joint registration and broad stone color, but its normal and roughness interiors are comparatively quiet and its grain has grown with the slabs. Rock05 diffuse contains useful aggregate variation, but is currently unused on the floor.

## Camera and filtering calculation

These use the 1536×1024 full/zoom capture contract, full vertical span `2*14.1/1.27`, zoom vertical span 17.6, and elevation .72 radians. Ground foreshortening is included. Values are analytical estimates, not captured GPU derivatives.

| View | Ground cm/pixel across view | Ground cm/pixel along depth | Current 0.333m Rock05 expected LOD | Proposed 2.4m expected LOD |
|---|---:|---:|---:|---:|
| Full | 2.17 | 3.29 | 7.06–7.66 | 4.21–4.81 |
| Zoom | 1.72 | 2.61 | 6.72–7.32 | 3.87–4.48 |

Formula: `LOD = log2(world_metres_per_pixel * 2048 / tile_period_metres)`. At 0.333m, one full-view pixel covers 133–202 source texels and the whole tile occupies only 10–15 pixels. Raising normal amplitude after sampling cannot restore that lost variation. Anisotropy helps the approximately 1.52× oblique footprint ratio, not the fundamental minification.

At 2.4m, a full-view tile occupies 73–111 pixels. Expected filtering lies mainly between 64² and 128² mips; 256² statistics alone would overstate full-view detail. Features 4–12cm wide occupy 1.2–5.5 full-view pixels depending on direction. The 8–12cm part of that band is a more reliable target for stable full-view breakup. Millimetre grains cannot individually resolve at this camera scale.

Tiles130 at 12.4×6.2m gives 3.027mm/source texel, expected full LOD 2.84–3.44. This is not excessively minified; its enlarged original texture content is the issue. Moving its UV to expose finer detail would also move photographed joints, so preserve this UV.

## Small CPU box-mip approximation

RGB values below are normalized stored channel values. Diffuse RGB statistics are in encoded sRGB, not linear radiometric averages. Normal RGB box resizing does not reproduce Unity's normal importer, renormalization, or GPU filtering. Roughness is genuinely 16-bit `I;16`; it was converted to float and divided by 65535, not converted directly to 8-bit RGB. These statistics establish retained image variance, not a native BRDF result.

| Resize | Diffuse RGB std | Normal XY std | Roughness std | Roughness min–max |
|---|---|---|---:|---:|
| 256² | .0669 / .0508 / .0411 | .0506 / .0462 | .02823 | .4748–.7500 |
| 128² | .0529 / .0412 / .0342 | .0415 / .0395 | .02372 | .4887–.7452 |
| 64² | .0397 / .0318 / .0272 | .0330 / .0334 | .01732 | .4956–.6600 |
| 32² | .0293 / .0239 / .0210 | .0253 / .0275 | .01021 | .4997–.5914 |
| 16² | .0203 / .0170 / .0156 | .0188 / .0209 | .00541 | .5068–.5359 |

Roughness mean is .517722 at all these resolutions. At 16² the current formula produces wet smoothness approximately .5445–.5939, with standard deviation .0092, rather than exercising most of the nominal .43–.73 range. At 64/128 the roughness standard deviation is about 3.2–4.4 times larger. This supports a meaningful 2.4m A/B candidate, while not proving that every retained feature falls within the desired 4–12cm band.

Rock05 normal mean remains near RGB (.5585,.5596,.9704) as it shrinks. The nonzero XY mean can retain a fairly consistent slope while local variation disappears; a broad normal tilt/sheening contribution is plausible. A future derived mineral-only normal could remove the broad scan plane before extracting local slopes, but the initial controlled comparison should keep gain 1.05 fixed so frequency and diffuse addition can be evaluated separately. Do not equate raw RGB normal mean with an exact measured world-space tilt.

## Coherent multi-scale recommendation

1. Keep Tiles130 authored UV at 12.4×6.2m, retaining photographed boundary alignment, large stone color trends and AO. Keep the actual fracture-plane geometry independent of this surface-layer diagnosis.
2. Test Rock05 color, normal and roughness together at exactly the same `worldXZ / 2.4` transform. This is a middle-scale photographed aggregate layer, not a replacement joint map. Local provenance identifies Rock05, Rob Tuytel, CC0 and source hashes, but records no real photographed surface dimensions. Therefore 2.4m is a camera-calibrated art setting, not a measured physical size.
3. Preserve Tiles130's large color structure. Use mean-neutral Rock05 diffuse modulation, preferably luminance-based or restrained chroma so the warm scan does not replace the courtyard palette. Normalize against the source mean in linear color space; encoded sRGB mean normalization does not guarantee exposure preservation. Filtering should preserve a modulation mean of one. This keeps the comparison focused on surface information rather than global brightness.
4. Match normal/roughness coordinates exactly to the color sample. Keep macro normal gain .40 and mid-layer normal gain 1.05 for the first comparison. Do not add independent random grain, unrelated roughness noise, global gloss, or an exposure adjustment to manufacture visible detail.
5. Keep valid mip filtering. Truly unresolved sub-centimetre grain should contribute to the aggregate reflectance response, not be forced into individual sparkling pixels with negative mip bias. If later needed, filtered roughness can account for unresolved normal variation; this is separate work requiring native motion validation.

The 2.4m proposal is preferable to the present 0.333m frequency for this camera and supplies a previously absent diffuse signal. It may also reveal repeated scan pits or broad color stains every 2.4m. If those dominate, derive a mean-neutral band-limited aggregate layer from all three registered maps rather than shrinking the same whole scan again. Do not randomize the maps independently. No source map derivative was created in this read-only task.

Minimal decisive native test: freeze geometry, camera, F0, wet mask, light and grade; compare current material against the coherent 2.4m three-map layer at full and zoom, at native 100% display scale. An albedo-only diagnostic and normal/roughness diagnostic help separate diffuse recovery from glints. If necessary capture runtime texture dimensions and shader UV derivative LOD. Then check a short motion sequence for shimmer. Success means stable few-pixel aggregate variation, preserved photo-joint registration, and no obvious repeated scan stamps. Actual improvement remains unconfirmed until this A/B.

## Reproduction

Run from workspace root with system Python and Pillow. This only reads maps and prints statistics; it writes no asset and starts no Blender/Unity process.

```powershell
@'
from PIL import Image, ImageStat
from pathlib import Path
from math import sin, log2
p = Path('Unity/Vesper/Assets/Vesper/AtmosphereV2/Textures')
for kind in ['diff', 'nor_gl', 'rough']:
    im = Image.open(p / f'rock_05_{kind}_2k.png')
    print(kind, im.mode, im.size)
    for n in [256,128,64,32,16]:
        if kind == 'rough':
            a = im.convert('F').resize((n,n), Image.Resampling.BOX)
            vals = [v/65535 for v in a.getdata()]
            mean = sum(vals)/len(vals)
            std = (sum((v-mean)**2 for v in vals)/len(vals))**.5
            print(n, mean, std, min(vals), max(vals))
        else:
            a = im.convert('RGB').resize((n,n), Image.Resampling.BOX)
            s = ImageStat.Stat(a)
            print(n, [v/255 for v in s.mean], [v/255 for v in s.stddev])
for name, span in [('full', 2*14.1/1.27), ('zoom',17.6)]:
    for mpp in [span/1024, span/1024/sin(.72)]:
        for period in [1/3, 2.4]:
            print(name, 'm/pixel',mpp, 'period',period,
                  'texels/pixel',mpp*2048/period,
                  'LOD',log2(mpp*2048/period), 'tilepixels',period/mpp)
'@ | python -
```

Inputs directly inspected: `.dream-loop/unity-atmosphere-v2/candidate-52/full.png`, `zoom.png`; concept image from the preceding structural comparison; `PavingV11/maps/Tiles130_4K-PNG_{Color,NormalGL,Roughness}.png`; imported original `rock_05_{diff,nor_gl,rough}_2k.png`. Local license/source record: `Migration/Source/AtmosphereV2/PhotographicStone/provenance-rock05.json`. Shader/build pointers above describe the read-time source; root is separately authorized to revise it after this diagnosis.
