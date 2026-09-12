# Native Windows input, A03

Connected Computer Use operated the actual visible1536x1024 D3D12 standalone window at192DPI. Window-relative screenshot coordinates were translated by the computer-use tool; production IMGUI and raw Unity input were both logged.

- Ground click: one native press/release, accepted at world(-0.74,0.80,-6.12),6.141m movement recorded.
- Drag: native drag changed camera angle, one drag and no additional click/movement.
- Wheel: one native wheel input registered and changed zoom.
- R: one explicit reset returned to initial position/framing.
- F9 saved the actual frame; F10 saved report and closed the owned player.

Evidence: `native-input-2/player.log`, `report.json`, `manual-start.png`, `manual-*.png`. Final counts1click/1drag/1zoom/1reset; no errors or movement safety stops. These actions were tool-driven native events, not the synthetic route probe. They do not constitute the user's physical mouse/trackpad acceptance. Continuous physical Shift hold was not verified by this native interface; synthetic run/walk checks are separate.

The first manual attempt was interrupted by an unrelated user-side installer elevation dialog. No input was sent to that dialog. Only this second attempt is claimed as completed native verification.
