# Final paving reprojection

The final mesh uses the fixed complete PavingV14 source, not the earlier V13 floor. Both fragment bottom support samples and all horizontal soil top vertices query the actual floor triangles. The ground's visual top is not assumed to be the navigation Y=0 plane.

| Root | Selected contact type | V13 floor height | V14 floor height | Change |
| --- | --- | ---: | ---: | ---: |
| 1 | Actual inner root vertex near parapet | -0.008254 m | -0.016126 m | -7.872 mm |
| 2 | Original measured terminal vertex | -0.059481 m | -0.025860 m | +33.622 mm |
| 3 | Original measured terminal vertex | -0.007761 m | -0.011525 m | -3.764 mm |
| 4 | Actual root/parapet contact | Wall projected | Wall projected | Unchanged |

Root 4's maximum-radius terminal sample is outside the floor at world X=9.823951. A horizontal patch there would have floated. The selected actual tree vertex 61633 meets the inward parapet near X=8.51; its small vertical pocket is projected to the precise retained V12 support stone, original node `592370d4-d68c-4fe8-b91d-41e1eaa41394`, instance 682. The source mesh, exact support Transform, source variant and original arrays are recorded in `world-contact-evidence.json`.

The build keeps the rubble XZ placement and four groups fixed while resampling height. Horizontal pocket tops are sampled just above the underlying paving and rise locally to meet their recorded root contact. Body undersides remain buried. The strict independent validator checks the exported closed geometry and full world bounds. This is authored visual contact geometry; it does not replace the existing root navigation hull or establish physical soil simulation.
