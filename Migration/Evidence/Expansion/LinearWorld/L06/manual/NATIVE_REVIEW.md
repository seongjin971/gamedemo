# L06 native input review

Verified on the actual Windows Unity player using the installed computer-use skill and `@oai/sky`. The selected window was uniquely identified by the L06 executable path, activated, and visually inspected before actions. Windows DPI192 renders the1536×1024 client within a770×542 window screenshot. Coordinates used the fresh window screenshot; runtime logs confirm focused IMGUI and raw input.

- Four actual native clicks accepted: initial lane, bridge25m to shore32.85m, abbey150m to156.21m, snow275m to281.11m.
- Directly observed movement animation, following camera and stopped arrival after each click.
- One drag rotated the camera; three wheel events exercised both directions; R restored starting position and default view.
- F6/F7/F8 were explicit fixture placements25/150/275, counted separately. They do not prove intervening traversal. Actual native movement distance26.41m.
- F9 saved unmodified Unity runtime screenshots after bridge, abbey and snow interaction: `manual-003004.png`, `manual-003148.png`, `manual-003330.png`.
- F10 saved the final report and requested player quit. `report.json`: clicks4, drags1, zooms3, resets1, fixtures3, rejected0, safetyStops0, errors0, AudioSources0.

Shift held input was not tested with the native key tool; the focused traversal separately exercises running state. This is agent-operated native input verification, not the user's final visual/playability acceptance. The generic report note about synthetic pointers applies to automated traverse mode; this manual session used actual native input tools.
