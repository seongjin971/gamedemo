# Preserved browser baseline

아래는 초기 브라우저 데모의 원본 설명입니다. 현재 Unity 개발 기준과 실행법은 [README](../README.md)와 [HANDOFF](../HANDOFF.md)를 따릅니다. 원본 요청과 자산 제한은 후속 Unity 작업 조건이 아닙니다. 과거 태그와 커밋은 원본 PC의 이력을 가리키며, 새 전달용 저장소에는 없을 수 있습니다.

## Preserved browser version

A live Three.js fantasy graphics demo made from the installed Dream Loop README's Example prompt. All models were authored locally in Blender or code. The slate texture and target reference were generated for this project; no stock models, textures, fonts, HDRIs, or other art assets were downloaded.

The browser version is preserved at Git tag `browser-baseline-2026-09-08` (`2413d5d`). The `unity-migration` branch adds a separate Unity URP comparison project in `Unity/Vesper`; see [Migration/README.md](../Migration/README.md) for its scene, controls, evidence and remaining work. `preview.png` continues to show the browser baseline.

## Run

```sh
npm install
npm run dev
```

Open **http://127.0.0.1:5173/** in Chrome. The server binds to loopback only.

```sh
npm run build
npm run preview
node --test
```

## Controls

- **Click** the courtyard: the knight walks there, navigating around obstacles.
- **Drag**: orbit the camera. Vertical dragging changes elevation within limits.
- **Scroll**: zoom in or out.
- **R**: return character and camera to the initial view.
- **H**: hide/show the interface.
- **P** or **Capture**: save a rendered screenshot and measurements locally during development; download a PNG in a production preview.
- **D**: show/hide diagnostic measurements.
- **B**: run a development render-throughput benchmark (separate from display FPS).
- **N**: benchmark orbiting-camera render throughput during development.
- **V**: save cached-AO versus freshly rendered AO comparisons for small orbit, walk, and zoom changes during development.
- **U**: export the loaded scene geometry, transforms, materials and a matching comparison capture to the local evidence sink during development. This does not modify the Unity project automatically.

The camera follows the knight slowly. Movement stays inside a small courtyard even though the ruined city extends far beyond it. This is a visual demo with no combat, enemies, objectives, or progression.

## Source Example, verbatim

> Build me a graphics demo: isometric camera, voxel-ish art style with realistic shading and reflective wet floors, a character in an interesting scene. Fantasy setting (think Elden Ring, Diablo). Three.js in browser, >60fps. Don't download assets. Time limit of 1 hour. Controls: click to move the character, camera lazy-follows; drag to rotate camera; scroll to zoom in/out. No gameplay for now. World should feel alive: motion, animations, subtle environmental behaviors. Area around player should look expansive, but only allow movement in a limited space. No need to confirm the art with me or ask questions, just go!

Source: `C:/Users/brian/.codex/skills/dream-loop/README.md`, Example section.

## Rendering and assets

- Orthographic camera, physically based stone/metal/cloth, generated stone and bark surface maps, custom chipped masonry, real planar wet-floor reflections, warm animated firelight, restrained bloom, and SMAA.
- Locally authored knight, gnarled tree and fractured stone in `public/models/`.
- Animated gait and cloak, breathing/head motion, generated flame sprites with animated distortion, rising embers, floating rune rings, drifting dust/haze and wind in grasses.
- Thousands of stones use instancing; distant geometry is simplified and does not cast shadows onto the playable court.
- Source modeling scripts, `.blend` files, generation prompts, concept target, screenshots, diagnostics and independent visual verdicts are retained in the ignored `.dream-loop/` directory.
- The far city is a generated panoramic matte that scrolls with orbit; the playable courtyard, surrounding nearer ruins, tree, knight and reflections are real-time 3D.

The frame counter reports measured browser presentation cadence. It cannot exceed the connected display's refresh rate. See `VALIDATION.md` for the measured result and remaining visual differences; a numerical or automated result is not user visual acceptance.
