# Native lighting diagnosis after candidate41

Baseline committed as `c857436`, independent6.0/Tier2, clean54.55–55.35FPS.
All outputs below are separate diagnostic evidence, not independent judge scores.

The player41 orbit frame0129 exposed broad silver glare across almost all paving.
Actual camera angle1.05980349, elevation.73530388, ortho11.1023626, position
(-27.1694241,31.0741272,15.9328890). `-vesperGlareOrbit 1` reproduces this camera
for the orbit image only. Default concept/slice comparison cameras stay intact.

The opt-in `-vesperDiagnostic` albedo/normals/indirect/moon/points modes separate
only AtmosphereStone rendering. Tree/character/effects remain ordinarily shaded;
water/sky and postprocessing also remain visible. These are visual component
diagnostics, not raw linear buffers or a full-scene additive decomposition.

Directly inspected real Unity outputs under `.dream-loop/unity-atmosphere-v2/`:

- `diagnostic-41-moon`: full/orbit. Black risers, cool lit treads.
- `diagnostic-41-points`: full. Orange riser bands remain in the point-light
  contribution; no distinct orange stripe exists in the source stone tint.
- `diagnostic-41-indirect`: full/glare-orbit. Low indirect contribution and
  visible independent pools; the broad silver glare is absent.
- `diagnostic-41-moon-glare`: glare-orbit. Broad silver paving glare reproduced
  in direct moon illumination alone.
- `diagnostic-41-albedo-glare`: glare-orbit. Neutral masonry faces and actual
  photographic floor boundaries; the orange bands are not albedo stripes.
- `diagnostic-41-normals-glare`: glare-orbit. Stair faces form repeated normal
  directions; the floor has detailed normals rather than a missing flat input.

Source inspection confirms per-pixel additional lights, single neutral stairs
material and monochrome vertex colors. Two orange point lights atY2, range6.7,
previously without shadows, light nearly every forward riser while upper treads
face away from lights below them. The old fixed normal.y-dependent indirect
term and top-only wet darkening amplify the contrast.

Diagnostic42 preserves all41 geometry and removes the second clear coat from
the scanned floor below the separate water plane. At the exact glare camera,
the broad silver layer disappears (`diagnostic-42-glare/orbit.png`, directly
opened). This supports the cause; it does not establish completed wet stone.
Stone normals now retain relief under wetness, and stone indirect illumination
uses scene spherical harmonics. Tree tint is20% darker in linear RGB. Fire
shadows improve occlusion but darken brazier bases too much.42 also emitted
Built-In-only shadow-resolution warnings and atlas downscaling warnings; these
are explicit follow-up fixes using URP Editor serialization, not ignored passes.

43 is testing localized shadowed fire, correct URP512 shadow tiers, restrained
local bounce, and point highlights on the actual water plane. New segmented
slabs, local masonry fractures and tree anatomy corrections are separately in
production. None has yet received a new independent visual score.
