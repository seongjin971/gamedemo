# P1 Mixamo motion improvement

## Latest authorization and source, 2026-09-09

The user withdrew the repeated-stage stop condition and explicitly requested actual Mixamo motion integration. The historical stopped attempt below is superseded. No new Meshy job was used.

Authenticated official Mixamo UI in connected Chrome supplied Walking (Walking With A Swagger, In Place unchecked), Breathing Idle and Stop Walking (Walking To Standing Idle). Downloads: FBX Binary, With Skin, 30 fps, keyframe reduction None, default overdrive 50 and arm space 50, Mirror false. Download events were registered before the final UI click; files arrived in the normal Downloads folder. Unarmed Walk Forward came from the user's existing 2026-09-03 download and is a comparison alternative.

prepared-01 retargets these motions onto the original P1 24-bone Generic skin with anatomical rest-pose correction. Original geometry, UVs, weights, bind matrices and material slots are unchanged. Root drift is removed for the existing movement owner. Selected Walk is Walking; Idle is Breathing Idle. Stop and WalkAlternative are retained for review but are not played by the two-clip runtime. Transitions use the existing distance-driven blend. Authored walking speed: 1.4826746285 source units/s, 2.668814 scene units/s at scale1.8. Full provenance and hashes: prepared-01/calibration.json.

Provider: https://www.mixamo.com/ . Usage reference: https://helpx.adobe.com/creative-cloud/faq/mixamo-faq.html . Raw sources are retained locally for reproducibility. The game contains retargeted clips. No credentials or signed download URLs are retained.

## Historical stopped attempt

User requested Dream Loop + Mixamo on 2026-09-09 after finding P1 walking awkward. Preserve candidate58 and delivered P1 build. Improve normal walking, settling and turning only; no P2, new character generation or courtyard rework. Stop and report if movement looks like walking on the spot, or repeated attempts produce no meaningful progress.

Baseline local commit: 3e0db76, clean on resume. No Unity/Blender/player running at resume. Existing runtime uses Generic skin and distance-driven clips. The baseline idle/stop is a simple blend and rear-foot repositioning is a known limitation.

Source route: original P1 prepared-v3 mesh -> export_upload.py -> Traveler-Upload.fbx -> official mixamo.com in connected Chrome, authenticated by user. No Meshy calls. Uploaded character is the existing user-authorized VESPER asset. Original geometry/UVs exported in its neutral pose without the existing armature; Mixamo is asked to rig this same character so its own motion can be used directly.

UI marker positions: chin, paired wrists/elbows/knees and groin, symmetry enabled. First request used No Fingers (25). UI returned to the marker step without an explicit failure message and reverted to Standard Skeleton (65). A single recovery request was submitted with the displayed standard skeleton; it also returned to Place markers without a rig result. The visible error/warning inspection did not establish the cause. Do not describe this as a proven topology or server defect.

STOPPED_BY_USER_NO_PROGRESS_RULE: after these two attempts, stop rather than repeat the same service workflow. No third retry. No animation was downloaded or integrated, no Unity scene/code/material was changed, and no new player was built. The delivered P1 build's full hash manifest was checked with zero mismatches. This is a service-workflow stall, not a finding about the quality of an implemented Mixamo walk. The open Chrome Mixamo marker page is retained for handoff. Another possible approach is to retarget a downloaded Mixamo motion onto the existing skeleton, but that alternative has not been started or validated.

Mixamo is a service source, not a new model generation charge. Raw downloaded motions and names/settings must be recorded here if obtained. Credentials and authentication URLs must never be retained.
