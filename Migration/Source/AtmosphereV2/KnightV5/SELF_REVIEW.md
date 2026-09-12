# Cloth v5 self-review

Status: ART_DIRECTED_CANDIDATE_READY_FOR_ROOT_VISUAL_REVIEW. This is not an untouched settled simulation or final Unity acceptance.

I inspected the completed top-level `preview-before.png` and `preview-after.png`, rendered at the same 800x900 resolution, orthographic camera, lighting, Cycles samples and AgX view transform. The top-level after image is the art-directed bake; the contracted raw final simulation preview is preserved under `attempt-03-flared/preview-after.png`.

Compared with v3 and the rejected v4 preview, the final v5 cape has softer uneven folds that drift sideways and change depth through the cloth, rather than three sharp repeated channels running continuously from collar to hem. A broad central cloth billow and smaller asymmetric relief remain visible. The lower hem has unequal shallow hanging curves. The upper collar is relatively smooth before the folds emerge below it. There are no visible holes, new armor intersections or obviously inverted patches in this review view. The armor and studio material appearance remain unchanged.

The raw physics failed the broad silhouette: final raw width was 0.34 m instead of approximately 0.71 m, and maximum movement across its final ten frames was about 5 cm, so static convergence was not established. Three failed simulation setups remain preserved. The final art-direction step restores the broad silhouette while retaining filtered simulation displacement, then sculpts small hem sags. This is a deliberate art-directed result, not a claim that the raw physics settled successfully.

QA: the final solidified cape width is 0.71379 m, compared with v3's 0.71252 m; height is 0.97780 m versus 0.99607 m, approximately 1.8% shorter. The new depth span is 0.45503 m versus 0.46270 m. Cape triangle count is 7,736, comfortably below 16,000, and exported vertices total 23,208. Maximum normal length error is 1.28e-7. Minimum triangle area is 2.68e-5 and minimum face-normal alignment is 0.70488, both positive. Finite arrays, valid indices, exact six-record preservation, other Blender mesh hashes, transforms/parents, material references and source hashes pass.

Limits: cloth still has the original smooth material without textile microdetail. The soft folds may lose contrast at the small full-scene character size, so the root must inspect a native Unity capture before integration acceptance. No Unity import, runtime or FPS test, animation changes, source asset changes or final adoption were performed here.
