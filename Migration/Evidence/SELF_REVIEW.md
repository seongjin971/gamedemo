# Unity first migration comparison — 2026-09-08

Status: **technical migration candidate; visual parity pending**. This is a self-review, not an independent Dream Loop score or user acceptance.

Compared the actual native `unity-slice.png` with `../Reference/unity-browser-slice.png`, both 1037 × 739, using the same orthographic camera target, size and reflected coordinate basis. The native evidence was recaptured in a fresh Editor process from the saved scene after correcting persistent volume overrides. No screenshot retouching or AI rendering is used as native evidence.

| Area | Observed result | Remaining work |
| --- | --- | --- |
| Layout | Knight, tree, walls, paving and braziers align closely; the source geometry is recognizable | Full-scene comparison and orbit framing remain |
| Stone | Authored chips, joints and source textures survive the bridge | Surface reads brighter/drier; warm reflective streaks are weaker than the browser |
| Reflections | Native buffer contains reflected knight, tree, masonry and fire; updates during Play | Tune the wet mask, normal detail and reflection contribution together; steps currently receive PBR highlights rather than separate planar reflections |
| Tree | Same branching and bark map; branch shadow is present | Match shadow softness/depth and bark exposure; inherited angular junctions remain |
| Knight | Hierarchy, red cloak and armor are retained; scripted movement works | Metal response differs; rounded shoulders remain an inherited modeling issue; direct motion review remains |
| Fire | Repaired Sprite positions/UVs produce visible animated flame sprites and flickering lights | Browser has richer bloom, warmer spread, embers and longer floor highlights |
| Background | Native distant masonry and reused generated panorama provide context | Haze is more uniform; panorama framing/parallax and deep foundations need work |
| Small effects | Static grass retains vertex colors; part of the rune pedestal is present | Rune line rings, drifting particles/haze, grass wind and browser UI are not fully ported |

The candidate is suitable for reviewing whether to continue from this native scene. It is **not ready to claim visual parity or submit as a finished full-target Dream Loop round**. The browser's previous 6.5/10 score is not transferred to Unity. Address the material/atmosphere differences, complete the agreed next native scope, and then use a fresh independent judge with full-target framing.

Technical reports accompany this file. Scripted render requests demonstrate execution, not display FPS. Unity Play mouse/keyboard feel, continuous camera/animation artifacts, the Windows player build, performance and final adoption remain open.
