# VESPER P1 running follow-up — 2026-09-09

User approved the walking direction with "좋아. 뛰는거도 해보자" after c2b23cd. This is a new bounded running addition following the completed walking delivery, not P2 map work. Dream Loop source/self/independent visual review applies without courtyard score loops. No new Meshy/Higgsfield generation is needed.

Official authenticated Mixamo UI in connected Chrome provided Running (description Running With Intention): FBX Binary, With Skin,30fps, keyframe reduction none, Mirror false, In Place false, Overdrive50, Arm-Space50,22frames. Downloaded2026-09-09 around15:01 Korea into Downloads/Running.fbx, copied here as Running-With-Intention.fbx. Provenance SHA-256: prepared-01/calibration.json. Source and licensing reference: https://www.mixamo.com/ and https://helpx.adobe.com/creative-cloud/faq/mixamo-faq.html . No raw source publication or credential retention.

Retarget onto the same24-bone Generic skin; preserve previous Mixamo Idle/Walk action hashes, geometry, weights, UVs, bind matrices and material. Run retains flight phases via a constant ground offset, rather than forcing a foot onto the ground every frame. Walk/Run align by phase offset0.975. Prepared source run speed3.8366997242units/s at model scale1; source stride2.685689807units, duration0.7s.

Runtime choice: hold either Shift while click-moving to run, release to walk; Shift does not create a destination or move a stationary actor. The user was offered Shift versus double-click; absent a preference, the stated Shift default is used. Selected scene speed5.4 versus walk2.25 (2.4x), acceleration7.5 versus5.5; phase-calibrated running playback is0.781922x at scale1.8. The source QA's original4.5speed example is a historical estimate, not the delivered runtime setting.

Only new P1Run components are added to the separate VesperAdventurerRun scene. Existing AdventurerMotor/camera/navigation remain unchanged; new input changes only that scene's motor instance, and new three-clip animation owns its visual. Gait uses actual speed and traveled distance, so sharp turns/braking return toward walking. No stamina/combat/terrain/NavMesh/map extension.

Preserve candidate58, initial P1, and c2b23cd Mixamo walk scenes, runtime/assets, launchers and build files. New normal launcher PLAY_VESPER_RUN.cmd points to Builds/VesperRun/VesperRun.exe. Direct Windows native input is unavailable in the connected tool surface, so automatic runtime commands and user input acceptance remain distinct.
