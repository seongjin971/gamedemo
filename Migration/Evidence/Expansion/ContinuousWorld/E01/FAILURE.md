# E01 final full-route failure, preserved

The first full-route pass stopped at d41.48 after9acceptedclicks/42.858m. Runtimeerrors0, but failures1/safetyStops1. This is **not a passing build** and was never promoted to the launcher.

Cause: D09 shoreline pullback placed the exact bridge endpoint at the shoreline vertex. A prior -.14m under-deck terrain cap also lowered that endpoint, so the adjoining terrain triangle descended to2.66m before the2.80m deck. The motor correctly refused the14cmunsupported step; NavMesh connectivity and the regional edge fixtures alone had not exercised this crossing.

Minimal E02 verification repair: remove the redundant endpoint height cap. The early River branch already lowers every interior riverbed vertex, while both exact endpoint vertices now remain at deck height. No motor tolerances, collision filters, input rules, artwork or quality scope were loosened. FullrouteQA mustrestart fromzero on a new separate E02build. E01build/source/logs remain preserved.
