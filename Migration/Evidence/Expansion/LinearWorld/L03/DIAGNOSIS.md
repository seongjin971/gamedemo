# L03 material diagnosis

Actual runtime diagnostic screenshots isolate depth, bounded opaque color, bounded planar reflection, and body color in `diagnostic/diagnostic-25-{1,2,3,4}.png`. Depth reconstruction and reflected tree/bridge geometry are present. The broad near-white water pattern is absent from the body and reflection channels but present in final lighting. Source inspection identifies the broad high-amplitude specular term (power650,amplitude.40); L04 changes this to1800/.028 with finer ripple detail. No old/shared shader was edited.

Stone diagnostic150-1 shows the fine texture is actually sampled but lacks the large-scale variation visible in the target. L04 combines the generated coarse limestone atlas with fine stone detail, uses its relief for normal variation, and blends settled snow on late path stones. It adds new Blender interlocking35-stone modules for the unpaved climates and moss texture in surrounding soil. These are rendered geometry/material changes, not edits to evidence PNGs.

L03 also verifies that automatic capture ignores native reset input (report.resets0). New scene audio sources were omitted per latest user steering. L03 diagnostic images are not visual-review screenshots and must never be scored as ordinary scene output.
