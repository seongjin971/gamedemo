# Atmosphere V2 source assets

These are additive derivatives of the preserved root `ArtSource` files. The
original files and browser assets are unchanged. Unity uses the exported JSON
here through `VesperAtmosphereBuild`, so rebuilding the candidate does not depend
on ignored `.dream-loop` exports. Mesh coordinates and triangle winding are
already converted for Unity. Do not convert them again.

- `Stone`: ten edited Blender stone variants, flatter faces and broad corner
  losses; JSON is keyed by the original bridge geometry UUID.
- `Tree`: curved branch derivative; original UVs and topology retained.
- `Knight`: seven mesh replacements for shallow shoulder plates, associated
  metal trim, and wider hanging cape folds. See `Knight/BUILDER.md`.

The source scripts can be executed with Blender `--background --python` from the
repository root. They intentionally regenerate the adjacent derivative outputs.
They never write the original root `ArtSource` files.

The generated mineral texture is stored directly in
`Unity/Vesper/Assets/Vesper/AtmosphereV2/Textures/stratified-stone.png`.
It was generated with the built-in image generation tool during this session
(1254 by 1254). Generation brief: seamless neutral charcoal stratified limestone
and slate base color, fine mineral pitting and shallow cleavage, no paving layout,
no baked lighting, no shiny highlights. It supplies mineral detail; wetness,
normal perturbation, reflections and lighting are computed by the Unity shader.

These are work in progress assets. Their inclusion does not establish whole-frame
visual target acceptance, direct interaction acceptance, or acceptable FPS.

## Additional derivatives after candidate17

- `TreeV8`: joined root/trunk sculpt with curved split offshoots;51,654 triangles,29,222 exported vertices. Replaces TreeV7 in the current candidate; both sources remain preserved.
- `StoneV7`: high-detail sculpt master and separate `runtime/` export. Use the runtime ten UUID JSONs:8,770 triangles total vs7,024 in V6. Exact source AABBs/transforms and export winding retained; see runtime QA. Existing directional grooves were largely a material issue; the new shader replaces legacy grain contribution and rotates mineral sampling per instance.

Two additional built-in ImageGen assets are stored under the Unity candidate's
`Textures` folder. They are runtime material inputs, never retouched evidence:

- `courtyard-wet-mask.png`: grayscale authored data mask with five irregular
  white pool footprints on black, narrow damp boundaries, concave bays and dry
  islands. Requested area12-16%; actual coverage must be checked in Unity rather
  than assumed from the prompt. Imported linear, Clamp, uncompressed.
- `moon-cloud-environment.png`:2:1 equirectangular nocturnal cloud panorama,
  blue-cyan/silver cloud openings, no ground, stars, objects or tiny exposed moon.
  Editor API converts this to an HDR cubemap; the reflection camera renders its
  sky while the primary camera retains the city backdrop. Runtime lighting and
  water mask determine its final contribution.

Actual generated dimensions `courtyard-wet-mask.png`: (1254, 1254).

Actual generated dimensions `moon-cloud-environment.png`: (1774, 887).


## Safe-stop additions after candidate23

- TreeV9 is now integrated: 74,671 triangles; bark plates, buttress roots and curved split offshoots.
- MasonryV8 is integrated: six asymmetric units and two low-cost facade course variants. Its script resolves the tracked StoneV7 input.
- PhotographicStone records Poly Haven Rock01 map provenance. Maps are stored directly in the Unity candidate Textures folder; albedo is sRGB, normal GL imported as NormalMap, roughness linear. Candidate27 became too smooth and is a diagnostic, not visual adoption. Rock05 remains downloaded only in ignored evidence.
- KnightV5 is integrated in candidate28 through the existing hierarchy/material-preserving mesh replacement path. Native static capture passed technical checks and the softer folds/uneven hem remain visible, but animation, player performance, independent visual review and user adoption are still open. See its INTEGRATION_STATUS.md.
- Old TreeV8, Stone derivatives, generated textures and all original inputs remain preserved.
