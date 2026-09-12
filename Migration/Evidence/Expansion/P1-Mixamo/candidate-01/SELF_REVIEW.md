# Mixamo P1 self-review — 2026-09-09

Ready for a bounded independent movement review. Target is the delivered P1 adventurer with visibly more natural Mixamo walking; candidate58 courtyard is accepted and is not being re-graded.

Opened full/zoom static captures beside P1 candidate03, plus actual player frames0042/0048/0054 (stride, braking blend, settled),0264 (near-root movement),0612 (close limit). Source Walk quarter-cycle and Idle renders were also opened. Same character geometry/skin/material and same courtyard/camera limits are preserved. The selected Mixamo walk reads more upright, with distinct forward boot extension and restrained opposite arm swing. No collapsed knees, detached limbs, big garment penetration or stationary walk continuation appears in these samples. Actual root travels25.41694 units and reaches six recorded route destinations. This supports actual integration; it is not a continuous realtime video review.

Stop is still a short blend to a wider breathing stance, with some foot repositioning. The downloaded Stop clip is not wired because playing its travel-dependent stopping steps at a stationary root would introduce sliding. No perfect foot-lock or authored start/stop system is claimed. Need independent check of adjacent walk/stop/turn frames for obvious regression, and isolated performance comparison.

Static capture produced all frames and a zero-error report but the old capture tool exited with native code-1073741819 during shutdown. An expansion-only fork with explicit render-resource/scene cleanup is being validated separately; actual standalone motion completed with exit0/errors0/skipped0/all-focused. No baseline source is changed by that diagnostic fix.
