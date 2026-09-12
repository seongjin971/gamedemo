# Boolean diagnostic

The first V13 preview exposed a missing stone. A whole-flight closed-mesh and winding check had passed, so that check alone was insufficient: a missing closed component can disappear without leaving a boundary. The rejected first result is preserved in `rejected-empty-stair-pass1` and must not be integrated.

The same `Carved stair 00-01` input was independently probed after welding normal seams and recalculating face orientation. Its signed volume was 0.1547757435 m3, with 333 vertices, 662 faces and zero nonmanifold edges. The finite cutter was also closed and outward oriented. Blender 5.2.1 returned these results:

| Solver | Result |
| --- | --- |
| Exact | Empty mesh, volume 0 |
| Exact with Self | 361 vertices, volume 0.1526572668, one nonmanifold edge |
| Exact with Self and Hole Tolerant | Same nonmanifold result |
| Manifold | 360 vertices, volume 0.1526572670, zero nonmanifold edges |

This identifies a reproducible solver/input interaction, not a proven general Blender defect or a proof that the source is free of every possible self-intersection. V13 uses the Manifold solver for the already closed staircase inputs. Architecture remains on its independently checked existing path.

The build now checks each of 90 stones before and after cutting: nonempty mesh, more than 90% original volume, and unchanged connected-component count after welding. The independent exported-JSON validator additionally requires all 90 original neutral color IDs, positive triangle cross-dot-normal, no degenerate triangles, finite unit normals, closed output from build QA, and unchanged V11/V12 source hashes. Eight architectural replacements also retain more than 99.3% of their corresponding V12 volume.

Diagnostic script and exact run log are retained under `.dream-loop/unity-atmosphere-v2/masonry-v13/probe_boolean.py` and `probe-boolean.log`. These checks prevent the observed missing-block failure; visual review remains a separate gate.
