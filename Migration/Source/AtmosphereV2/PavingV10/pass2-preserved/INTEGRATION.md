# Paving V10 integration contract

This source package replaces only the courtyard ground paving. Use the final `paving-v10-report.json` selection manifest to verify all 430 removals. Keep the source stair treads, stair lips, upper landing, and separate trim instances.

For the existing `InstallStone` pipeline, skip `AppendStone` only when all of these are true:

- Source node is not distant and has an existing StoneV7/runtime geometry.
- `node.materials[0] == "1ba07011-f8c4-4d07-9550-6d031350c67f"`.
- The instance passes the existing selection bounds: original Three position X in [-10, 10], Z in [-13, 22], Y in [-3, 15].
- `instance.position[1] < 0.2`.

Build the remaining source batches normally, then add `paving-v10-mesh.json` once at identity position/rotation/scale. The mesh already contains Unity world positions, normals, and reversed Unity winding. Do not apply the bridge's additional X reflection. It uses one material with the existing floor material identifier above and layer 29, matching the prior floor reflection mask.

The JSON extends the ordinary Geo schema with `colors`, a flat RGBA float array. Assign one `Color(colors[i*4], colors[i*4+1], colors[i*4+2], colors[i*4+3])` per vertex. These are mild multipliers centered on the measured old instance-color mean; they are constant across each stone. The shader must consume vertex color just as it does the current combined paving batches. Positions/normals have stride 3, UV stride 2, and indices stride 1. Use UInt32 indices, then recalculate bounds and tangents, preserving the provided normals.

The carved ground nominal level is the median actual V7 source top, -0.0317635536 m. Shallow face variation remains below the separate water surface at Y=-0.004. The original source has a wide rear staircase void and missing rear paving patches; the report records their row segment footprint. The front courtyard is repaved within the exact original outer AABB envelope. Old internal gaps and tiny outer scallops are not preserved individually.

The blend contains hidden original ground meshes plus the authored replacement, with matching neutral preview cameras. These renders inspect geometry. Final scene lighting, water interaction, movement, FPS, and user visual acceptance require Unity review.
