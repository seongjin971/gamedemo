# D09 isolated effect cost

1536×1024 windowed D3D12, Intel Arc 130V, no concurrent Unity Editor/Blender/other game player. Twelve 6-second recorded intervals after warmup, 0 unfocused frames and 0 runtime errors. Values are natural frame cadence, not display-present/GPU timestamps. Each variant disables one group; 'shadows off' disables the main sun shadows while ambient occlusion remains. The 120 FPS cap limits interpretation of faster variants.

| Fixture | All FPS / p95 ms | Reflection off FPS | Precipitation off FPS | Sun shadows off FPS |
|---|---:|---:|---:|---:|
| River 48 | 108.53 / 10.60 | 118.00 | 106.23 | 119.96 |
| Abbey 180 | 103.12 / 11.36 | 119.95 | 106.01 | 119.97 |
| Snow 342 | 117.31 / 10.63 | 118.84 | 115.36 | 119.94 |

Reflection and main shadows are the larger measured costs in river/abbey views. Small negative precipitation deltas are sampling variation; they do not show that particles make rendering faster. The snow reflection toggle is essentially a control because both local planar reflections are already inactive there. This is a diagnostic D09 comparison, not a replacement for final E's five fixtures × static/walk/orbit/zoom performance run.
