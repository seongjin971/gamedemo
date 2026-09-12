# P1 novice adventurer

User authorized implementation on 2026-09-09. Candidate58 is the accepted courtyard baseline; no environment polish or P2 work is part of this package.

Time budget added by the user: 2h20 from 03:43:13 UTC, deadline 06:03:13 UTC (15:03:13 Korea time). Deliver the playable P1 package within this budget.

Meshy: maximum three submitted generation/rigging/animation jobs in total, including the first model job already submitted. Read-only status/download requests are not new generation jobs. If further Meshy generation becomes necessary to avoid a noticeable quality loss, explain the concrete need and request approval before submitting it. User allows ample Higgsfield use when useful. No other project is modified.

Design: lean adult novice traveler, short chestnut hair, exposed face, oatmeal linen tunic, brown leather vest, taupe trousers, mid-calf boots, short petrol teal shoulder shawl, compact backpack and one belt pouch. These are implementation art choices, not user-specified identity facts. Original built-in imagegen reference: `reference-adventurer.png`.

Reference prompt (normalized): one realistic in-engine full-body novice traveler, natural proportions, face and short brown hair visible; oatmeal tunic, worn brown sleeveless leather vest, dark taupe trousers, leather boots; short teal shoulder cloth above waist, compact brown backpack, belt pouch; no armor, no ornate decoration. Relaxed separated A-pose limbs, single character on medium-gray background with neutral studio light. Readable clothing layers and sewn cloth folds, restrained high-quality game textures. No layout text or secondary views. Suited to the accepted moonlit VESPER courtyard.

Source: OpenAI built-in imagegen output created for this task, then Meshy7 Ultra model generation. Meshy request/status/manifests are recorded beside this file. Signed URLs and credentials are excluded. Blender is used for inspecting skin, preparing in-place clips and exporting Unity-ready assets.

Completed external requests: model `01a08441-3151-7407-96a3-0edcd37e48c3` (35 credits), rig `01a08444-c3ac-703d-ba36-07284b96a903` (5 credits), idle `01a08446-80a7-7637-9de2-8fa010b20dca` (3 credits). Total 3 jobs / 43 credits. No Higgsfield generation has been needed. Rig and animation contracts were checked against [Meshy rigging](https://docs.meshy.ai/en/api/rigging), [animation](https://docs.meshy.ai/en/api/animation), and [idle action 0 library entry](https://docs.meshy.ai/en/api/animation-library).

Live tool availability: Meshy authenticated balance read succeeded (`connection.json`). Higgsfield CLI is installed and its authenticated account status read succeeded (`higgsfield-connection.json`); no generation was submitted to it. Personal account details were not retained. No tool substitution required accepting a visibly worse character.

Blender derivatives are retained in `prepared`, `prepared-v2`, `prepared-v3`. V2 replaces the supplied staggered idle with planted rest legs, lowered arms and restrained upper-body motion. V3 reduces excess lateral upper-arm spread during the supplied walk; lower-body source trajectory is preserved. No Humanoid retargeting or physical cloth simulation is used. The shawl, pouch and backpack are part of the skinned character and move with the same skeleton.

The 1.78m source is displayed at 1.8 scale to fit the accepted scene's oversized character art scale (baseline renderer bounds about 3.50 high). The motor retains the original 2.25 scene units/s cruise speed. The animation clock uses the calibrated source 1.5245m/s times visual scale, so foot cadence follows actual traveled distance. The default camera is preserved; closer zoom blends toward the character. A modest custom ambient probe supplement applies only to this skin, with no global light/material change.

Native Windows Computer Use reconnect at task start failed: `Computer Use native pipe is unavailable ... os error 2`. No repeated permission request. Automated player screenshots/motion are not direct pointer input or monitor-present FPS.
