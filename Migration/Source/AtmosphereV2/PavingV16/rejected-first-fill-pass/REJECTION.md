# Rejected first fill pass

Mesh hash `2615d88470252f741f3204d1bbe097fe043a566c98f92ba8e5bef016ba4dfc72`.

The ten angular slab bodies passed closed/winding/projected-area checks. An additional exact XZ intersection check found that fill96_3 overlapped neighboring stone97 and fill97_7 overlapped stone120. The weaker original point-probe overlap test missed crossing edges. The final builder uses full segment/containment polygon tests and omits those two fills.

Direct review of the first neutral zoom also found that the rectangular fill end faces looked like small support plates. The final fill tapers both ends and the outer edge below the exact original bed surface, instead of exposing rectangular ends. Stone geometry remains the same.

The eight actual first-pass previews and this mesh/blend/metadata/failed QA are preserved here. Their `before-v15-*` images remain the exact unchanged baseline for the final four after-only renders.
