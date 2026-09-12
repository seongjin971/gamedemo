# Camera-safe broken abbey masonry

New additive wall/pier assets responding to the exposed empty front and side of C03's abbey. These are actual broken masonry profiles, not vertically scaled intact window modules. Existing chapel assets, scenes, code, textures and builds remain untouched.

`CW_ChapelBrokenWall6m.fbx`:4,357 triangles. Body6m wide,.6m deep; tallest surviving left end2.8m. Broken courses descend through roughly1.9m and1.3m to a low .6-.9m remainder, with a slanted final toe. Small attached rubble extends the total depth to1.3m, so account for that toe when keeping the central walking gap clear. The wall includes actual individually bonded chipped stones, recessed mortar, surviving lancet sill/jamb fragments and broken vertical moldings. Moss lies primarily in damp joints. The source profile and29 sampled silhouette heights are recorded in the manifest/audit.

`CW_ChapelBrokenPier3m.fbx`:2,906 triangles, exactly3m high. Actual footprint is approximately.91x.88m, under the requested1m square. Eight engaged Gothic shaft fragments surround the bonded center; carved base bands, binding collars, an irregular fractured top, sparse moss and a compact rubble toe anchor an opening end.

Both pivots are ground center0, sourceX width/sourceY depth/sourceZ up. Preserve the imported -90 degree X FBX root conversion; put world position/yaw/scale on the parent's wrapper. For the wall, the high end is source negativeX; rotate the instance to choose which side remains tall.

Materials are `CW_ChapelStone`, `CW_ChapelStoneLight`, `CW_ChapelMortar`, and `CW_WetMoss`. UV0 remains0..1 per material. The existing parent Chapel rule can map the stone materials to WorldSurfaceAtlas top-right. `CW_WetMoss` deliberately omits Chapel/Crevice in its name so the parent's existing Moss rule selects the vegetation/soil quadrant. The preview material is an inspection treatment; final wetness/palette are parent-owned.

`generate_chapel_broken.py` builds the source and exports only to `staged/`. `audit_chapel_broken.py` reimports those files and verifies exact triangle counts, zero degenerate triangles, finite geometry, per-material UV bounds, original coordinate bounds and root rotation. Both passed. The stable batch was copied into the new Art/EnvironmentKit/ChapelBroken folder during the parent-provided C04 no-build window; copied SHA256 hashes match the staged files. Source scripts, blends and final previews remain outside Assets.
