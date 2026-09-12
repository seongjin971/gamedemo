# First running probe: route was too short

The first automatic run completed without runtime exceptions, screenshot loss or clearance errors. It reached5.4units/s on the longer near-root route and stopped correctly. Three expectation checks failed on the3.36-unit home-to-(0,10) route: full run after initial walking, full run before stop, and sustained walking after Shift release. Acceleration/braking occupied that short route, so it could not reliably exercise the intended cruise transitions.

The probe and continuous performance route were changed to home-to-(4,6.7), an existing valid longer courtyard route. No animation, input, speed or movement implementation was changed for this QA correction. Candidate02/player02 records that verification. The original failed report is retained rather than relabeled as passing.
