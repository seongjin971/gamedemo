# Material isolation

D06 is a diagnostic rebuild of the saved D05 scene, with diagnostic shader channels and the manual-input probe. It is not a new prepared geometry revision and is not the launcher candidate.

The eight unedited `materials` captures isolate albedo, normal and wetness. Abbey slab normals are uniformly upward, while the repeating broad white lobes exactly follow the sinusoidal wetness field. D07 replaces that field with nearly uniform grain-modulated wetness, lowers floor reflection and keeps puddles separate. Snow vertex channels show a valid diagonal route mask; D07 increases its visible contrast and refines terrain sampling.

The diagnostic report records4errors from attempting `Material.mainTexture` on shaders whose property is `_BaseMap`. The diagnostic accessor is corrected to `GetTexture("_BaseMap")` in D07. These errors belong to diagnostic logging and are not claimed as a passing run. D07 regular capture has0errors.
