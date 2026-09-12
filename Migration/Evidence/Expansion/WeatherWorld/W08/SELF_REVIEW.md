# W08 structural and flash candidate, shelter cutaway follow-up

Actual FHD peak images visibly strengthen flash. Approximate 8-bit grayscale averages: W06 default74.46 -> W08 default108.91; W06 strong86.79 -> W08 strong127.62. Normal44.24 and recovered44.25 remain essentially equal. Multiplicative screen pass creates the visible improvement; W07 numeric exposure change alone had not.

However, the sheltered still obscures the upper player rather than showing the intended transparent roof. URP transparent shader keyword was set only at runtime while every referenced roof material was authored opaque; retain a serialized transparent material variant in separate W09, with runtime opaque initialization outside shelter. Do not claim W08 shelter visibility accepted from a boolean shelter activation check. W09 will compare actual pixels again.
