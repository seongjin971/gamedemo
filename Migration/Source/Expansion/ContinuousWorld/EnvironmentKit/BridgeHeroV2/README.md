# B07 waterside structure revisions

New additive assets responding to B07's missing arch / paved approach / fine reed silhouettes. The older BridgeHero, shared atlas, existing assets, Unity code and builds were preserved. Art exports are complete and frozen after the ReedBand internal-node warning fix. All Blender processes stopped before parent performance verification.

## Open bridge

`CW_StoneBridgeHeroV2_14m.fbx`: 17,663 explicit triangles, source bounds X[-3.25,3.25], Y[-7,7], Z[-3.02,1.34]. Same nominal deck pivot0, 14m length, 6.5m exterior width and 5.2m clear walkway. Highest paving vertex is +.007893, with a parent-owned smooth walking collider. Preserve imported -90 degree X root conversion and place by an outer wrapper.

The real curved clear arch spans9.8m along the bridge. Intrados crown is -.22 relative to deck; springline is -3.0. End piers extend to -3.02. Ten horizontal arch-through rays and forty walking rays pass after FBX reimport, with zero degenerate triangles. Radial voussoirs and fitted spandrel courses remain actual geometry.

Forty-two broad pavers replace the earlier63: mean slab area is about50% larger (roughly22% greater linear size). Paving UVs crop a .46-wide region instead of .95, reducing texture repetition frequency by about half. The original atlas's crack contrast remains present; parent material/shader tuning is still needed if lower contrast is desired. UV0 stays within0..1 and existing `CW_BridgeStone`, `CW_BridgeStoneLight`, `CW_BridgeMortar` slots accept the stone-quadrant ST.

`bridge-dry-preview.png`, `bridge-current-water-preview.png` and `bridge-lowered-water-preview.png` were inspected. The latter two use water at -1.25 and -1.75 relative to deck, corresponding to world water -.45 and -.95 when the bridge deck is world+.8. The lowered-water preview exposes a clearer curved opening. The fixed flat deck and high camera continue to limit apparent arch height; these are asset previews, not a new independent scene score.

## Paved approach

`CW_BridgeApproach6x8m.fbx`: 1,192 triangles, 25 broad irregular slabs, nominal6m width by8m length. Chipped perimeter stones sit slightly inside the nominal footprint. Pivot is nominal deck center0, broad top faces0..+.008, underside-.16, no walls. Parent owns the continuous collider and ground support. Twenty-five slab-center rays pass after reimport. Same calm stone UV crop/material slots as the new bridge.

## Evidence and companion reeds

Reproducible generators and source blends are here; `fbx-audit.json` and `additions-fbx-audit.json` contain final import checks. All four new exported files pass explicit triangle, UV range, degeneracy and alignment checks. The companion golden reeds and its own source/preview are in sibling `ReedBand`.
