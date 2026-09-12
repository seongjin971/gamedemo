# Candidate45 diagnostic, not judge-ready

Actual Unity full/orbit/zoom/slice were opened directly. PavingV12 replaces the
continuous V11 mesh with a lower-density bed and 24 closed photographic slab
bodies. Their edges are clearer, but isolated raised stones still sit on a flat
surround. This reads as scattered stepping stones, not a coherent paved court.
PavingV13 is expanding the neighboring photographed stone bodies; V12 remains
preserved. The prior lighting, water and effects changes remain under review.
Stair bands, shallow cloudy pools and modular portal damage remain blockers.
No new independent score is assigned. Latest independent review remains
candidate41 at 6.0/10, Tier2.

## Controlled natural-frame cost isolation

All four runs used the same player45-diagnostics binary, 1536x1024 windowed,
FrameTiming disabled, no explicit render requests, and the same static/walk/
orbit/zoom sequence. No other Unity, Blender or heavy asset validation ran.
Every segment was focused and every runtime error list empty. This does not
verify desktop occlusion, monitor presentation cadence or direct user input.

| Runtime override | Static | Walk | Orbit | Zoom |
| --- | ---: | ---: | ---: | ---: |
| Default soft fire shadows | 32.201 | 32.316 | 31.870 | 32.017 |
| Fire shadows disabled | 55.550 | 56.568 | 55.581 | 56.112 |
| Hard fire shadows | 32.421 | 32.750 | 32.400 | 32.569 |
| Ground shadow casting disabled | 32.010 | 32.246 | 31.966 | 32.048 |

These toggles isolate the large cost to additional fire shadows; switching
filter quality or removing the ground caster does not recover it. They do not
yet isolate shadow-map rasterization from shadow sampling. Disabled-shadow and
hard-shadow runs are diagnostics, not adopted visual candidates. Build report
for this binary recorded zero errors and zero warnings after replacing an
obsolete FindObjects overload. Walk includes time stopped after arrival.

Next: test exact local shadow geometry, retaining visible meshes and main-moon
casters, alongside the source-reviewed stair correction. Then compare actual
renders and measure again. A code optimization is not a verified win until then.
