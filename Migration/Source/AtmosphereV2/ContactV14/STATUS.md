# Ready for native Unity comparison

The final source uses complete fixed PavingV14 geometry, SHA256 `00ee641f13bdc841a4d0fd531379380a33952ee8f952133e750380e9e4be5c59`. Fragment supports and horizontal pockets have been reprojected to its actual triangle heights. TreeV12 and PavingV14 sources remain unchanged.

All five final 1536 x 1024 images were directly inspected: `overview-before.png`, `overview-after.png`, `clusters-before.png`, `clusters-after.png`, and `contacts-after.png`. They use the intact tree and complete floor. Earlier cropped context images remain in `retained-first-context/`; those are not final context evidence.

The independent validator was rerun against the final exported files and passed. Exactly 50 old loose offcuts are selected for removal and 49 retained. New geometry comprises 26 closed fragments in four groups and four closed contact deposits, totaling 1,084 triangles. Measured fragment diameter ratios within each group range from 2.856 to 3.319.

- Rubble SHA256: `7edb648a785c17c25611014ed090792e0b00888ea7d299ac5eb0c4ae808d87c8`
- Deposits SHA256: `db43062755e611af95441466b4c55dc7d9a998ce2ace3e14c5aba41d5763026e`

No further geometry or render changes are planned. This is a source handoff for native comparison, not visual adoption, a Tier 3 pass, or a performance claim. Material grain, partial contact occlusion and native visibility still require Unity review. See `SELF_REVIEW.md` and `INTEGRATION.md`.
