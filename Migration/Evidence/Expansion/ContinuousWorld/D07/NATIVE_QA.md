# D07 native Windows input

2026-09-10 05:01-05:09 KST. Connected Windows Computer Use (Sky) targeted the D07 VesperWorld window; Unity rendered1536x1024 while the Windows capture displayed at770x542 including its frame.

- F6/F7/F8 explicitly placed local river/abbey/snow fixtures. These3placements are not seamless traversal.
- Three actual Windows mouse clicks reached visible walking surfaces: bridge6.509m, abbey9.093m, snowy downhill3.006m. Total18.608m. Logs retain native raw and IMGUI events, screen rays, collider, destination and player positions.
- A fourth click on the gray face below the bridge was rejected. Its hit was `Continuous terrain -16 -64`, world(-10.40,-0.30,-53.61), normal(0,.13,.99). This also identifies the terrain bank as the remaining arch-view occluder.
- One actual drag changed orbit without adding a click; one wheel event changed zoom. R explicitly returned to(0,.8,0) and restored the default camera.
- Shift+F9 produced one observed native Shift frame and two state changes. Native running distance was0: this does not establish sustained Shift-held movement. Physical trackpad and user feel remain untested.
- F9 screenshots and the manual/report.json/player.log preserve evidence. No runtime errors or movement safety aborts were recorded.

This is operating-system input automation, distinct from the synthetic screen-coordinate regression probe and from user acceptance.
