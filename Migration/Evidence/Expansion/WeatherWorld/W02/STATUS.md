# W02 — incomplete runtime candidate, not delivered

Build succeeded with zero reported errors/warnings. Actual FHD capture completed forest/rain/flash frames, then UnityPlayer crashed while entering the first snowy fixture. Snow visuals, movement and performance are unverified for this build. Preserve the failed capture and player.log; do not treat its partial report (zero managed errors) as a passing run.

W03 removes snow particle world-physics collision as a bounded diagnostic/stability correction. Surface depth occlusion and existing shelter masks remain; player/road physics is unchanged. The W02 stack did not provide enough symbols to establish a definitive root cause. W03 must pass actual snow rendering and final runtime checks before delivery.
