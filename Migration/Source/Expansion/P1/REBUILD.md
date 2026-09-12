# Rebuild delivered P1

The playable build is already present. These are maintenance instructions, not a request to regenerate Meshy assets or start P2. Never run the old atmosphere/migration scene builder for this expansion.

Use this workspace only, Unity6000.5.7f1, and one Editor process for `Unity/Vesper`. Close the P1 player before replacing its build. Existing `prepared-v3/Adventurer.fbx` and Unity `Expansion/P1/Art` assets are the delivered sources; rebuilding does not require an external service. `prepare_character.py` is the retained Blender conversion/correction script, and `stage_unity_art.py` stages the latest prepared FBX and packed PBR maps. The .blend files and originals are retained for editing.

Unity Editor entry points:

- `Vesper.Expansion.Editor.AdventurerBuild.Prepare`: import through ModelImporter/TextureImporter, create expansion material and save a new expansion scene from the accepted courtyard. This replaces the P1 scene, so run it only when intentionally rebuilding P1. Supply `-p1Output` with a new evidence directory to preserve earlier evidence.
- `Vesper.Expansion.Editor.AdventurerBuild.Build`: build only `Assets/Vesper/Scenes/Expansion/VesperAdventurerP1.unity`. Default output `Builds/VesperExpansion/VesperAdventurer.exe`, relative to the Unity project. Original `Builds/VesperPreview` is not the output.
- `Vesper.Expansion.Editor.AdventurerPortrait.Run`: optional diagnostic close capture. It does not save the scene. Supply a new `-p1Output` directory.

For batch execution use `-batchmode -projectPath "<workspace>/Unity/Vesper" -executeMethod <entrypoint> -logFile "<new log path>"`. These entry points exit themselves; capture callbacks must not be interrupted with `-quit`. On Windows launch background Editors with `Start-Process -WindowStyle Hidden`, and wait for one to finish before starting another. Capture `$process.Handle` before `WaitForExit()` when checking PowerShell process exit codes.

Player options, each in a separate visible1536×1024 windowed run:

- `-p1FunctionalQA "<new output>"`: automatic route, rejection, reroute, clamp/reset checks, then exit.
- `-p1MotionQA "<new output>"`: automatic recorded movement and camera sequence, then exit. `review_motion.py <output> --video` can encode afterward using the retained local ffmpeg; do not encode during performance measurement.
- `-p1QA "<new output>"`: natural frame-cadence comparison,5s warmup and8s per stage, then exit. No FrameTiming instrumentation by default. Run the original player separately with `-vesperQA` for a current baseline.

All these are opt-in QA components. The regular launcher has none of these flags. Automatic commands do not count as real input. Avoid heavy parallel work during performance checks. See the delivered validation record for API, resolution, results and limitations.

`meshy_character.py` maintains an exclusive submission marker and a three-job cap. Its credential reader is a read-only helper in the user's existing `2ndKoreawar/Tools/Meshy` folder; it never calls that helper's main function or edits that project. Credentials and private signed URLs remain outside tracked output. Do not rerun generation to rebuild the supplied FBX.
