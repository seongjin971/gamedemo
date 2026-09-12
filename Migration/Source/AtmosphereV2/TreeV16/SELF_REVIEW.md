# TreeV16 direct source review

Status: READY_FOR_NATIVE_CANDIDATE. The bounded source derivative and supplemental covers are ready to integrate for comparison. This is not final native visual acceptance, reference parity, or navigation approval.

I directly opened the corrected full-before/after, zoom-before/after and glare-orbit-before/after images, plus the matched auxiliary root close-ups. Reference context was concept.png and native candidate52 full/zoom/glare, with verdict-unity-8. The first geometry pass was visibly too broad at the root feet and was retained without adoption. The final source narrows the three floor-root corridors earlier, compresses their raised profiles and buries the terminal sections. The fourth root turns/retracts inward rather than extending past real floor support.

In corrected full and zoom, the foremost foot-shaped protrusion becomes a narrower attached root descending into the paving. More floor is exposed beside it. The rear-right buttress also loses its raised terminal lip. In glare-orbit the front root ends at the paving rather than curling over it; the broad lateral buttress remains visible but its end is lower. There is no exposed horizontal cut cap, detached sleeve or new open transition visible in these views. The three small covers sit near the ends; burial is driven by tree geometry, not by their color.

The two lower horizontal forks are visibly slimmer across their broad bark masses, and the supporting negative spaces open slightly. Their attachment to the trunk remains continuous. Fine existing ramification and bark ridges remain legible. The upper fork changes less, and the overall tree still has a bulky, sculpted trunk; this pass does not make it identical to the concept. Some short bark spikes remain intentionally. The source's shallow-depth limitation also remains; no unrestricted360-degree quality claim is made.

The root system still has substantial attached flanges. It is not reduced to four clean cylindrical roots, and the broad side buttress can still read heavy from glare-orbit. The retained Contact14 brown deposits are plainly polygonal in neutral Blender lighting and become more visible after narrowing. Native review should check whether their layering with the new small earth pieces looks excessive; no earlier object was removed. Cover silhouettes and actual foot/root crossing must be judged in Unity. Neutral context omits portal/stairs/knight/sky, and its lighting/materials are not the Unity stack.

## Checked evidence

- Final tree:157999 triangles,136927 exported vertices. Original triangle topology and per-triangle UVs are exact. White tree vertex colors, upper crown above localY4.9, total width6.3m and top6.34m are preserved. Every protected source hash remains unchanged.
- Two lower whole-section outer95th-percentile radii reduce18–19%. The third upper region measures11–19% because the upper-crown preservation fade intersects it. Forty of119 detected separated short-spike candidates retract; no new spikes or global smoothing are added.
- All546 selected exposed terminal source vertices have actual floor/parapet support and at least45mm clearance beneath their corresponding support. The corridor selection and non-exhaustive coverage limitation are explicit in INTEGRATION.md. No radial enlargement was added. Minimum sampled spatial Jacobian is0.1287975, positive at all133345 original source vertices.
- All finite/index/area/unit-normal checks pass. Face/mean-normal dot is strictly positive for every triangle; minimum normalized alignment is0.00039818, a small positive margin. Export uses131 face-normal fallbacks. The result does not warrant claiming perfect source shading everywhere.
- Supplemental geometry is3 stone covers plus3 earth pieces,144 triangles total, separately exported in native world space at identity. All are closed, have positive volume and strict positive normals. The fourth root uses retained parapet cover.
- The30-point root hull is derived from the final mesh in native-local meters at Y[-0.005,0.7]. Native installation must regenerate/audit navigation with exact TRS and character clearance, including the small covers.

## Projection correction

The initial full/zoom/glare renders were horizontally mirrored relative to Unity because an orientation-preserving coordinate bridge was combined with a right-handed Blender look-at. They are retained under retained-mirrored-context, and their before/after comparison is valid only as source comparison. The root close-ups also retain that auxiliary basis; they are not native camera captures.

Final full/zoom/glare images were regenerated from the actual3D context after a render-only world-X reflection and a rebuilt camera. The tree is now on the same left side as native full. All18 independently computed native-world landmark viewport checks pass, maximum error2.95314e-7, and native orthographic vertical span is asserted. This verifies handedness and the supplied camera parameters; it does not equate Blender appearance to Unity. Rendering did not alter any final mesh/JSON/material source file. The corrected batch saved all6 images and printed normal Blender completion; the PowerShell wrapper reported exit1 from Blender's material deprecation warning, with no Python traceback or failed projection assertion.

All implementation, QA, final source, retained failed evidence and previews are confined to TreeV16. INTEGRATION.md is the authoritative schema/TRS/hash handoff. Native full/zoom/glare comparison and near-root walking remain the next gate owned by the parent agent.
