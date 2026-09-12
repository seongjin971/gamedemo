# Masonry V11: structural diagnosis

Status: source analysis followed by parent-authorized stair production. The final source is ready for native integration comparison; it is not visually adopted. No Unity asset, original source, scene, material or instance was modified.

Directly inspected `Migration/Reference/concept.png`, candidate-36 `full.png` and `zoom.png`, `verdict-unity-6.md`, and the V8 neutral-clay after render. The target still contains regular stair levels and masonry courses; their stone blocks read as continuous bodies, with irregular joints, shallow open losses and light-supplied warmth. Candidate 36 divides each stair level into a bright warm vertical strip and a separate dark blue horizontal strip. Its piers repeat the same protruding shoulder under almost every stone.

## Established source causes

- `src/world.js:155` builds 10 stair levels. Each level has a dark support, nine stone risers (0.863 x 0.2784 x 0.17 m), nine separate floor-material treads (0.863 x 0.07 x 0.49 m), then nine or ten additional thin floor-material lips. Riser and tread joints share exactly the same nine column positions on all 10 levels. Candidate builder only removes/shortens some lips; it retains aligned tread/riser joints and the two material families.
- Preserved bridge stone tint is (0.4793, 0.4735, 0.4233), whereas floor tint is (0.3185, 0.3968, 0.4621). Candidate builder multiplies both by 0.70 and floor by another 0.75, leaving stone at approximately (0.3355, 0.3315, 0.2963), floor at (0.1672, 0.2083, 0.2426). Vertical risers therefore have a warmer and brighter base, even before orientation-specific ambient and local fire light. Instance color variation is nearly neutral and is not the principal brown stripe.
- V8 variants preserve a broad continuous sloped shoulder below the top face. Compressing these normalized meshes into short courses repeats that slope as a dark horizontal line. Added local concavities and corner cuts do not remove this shared profile.
- Original portal piers retain 0.575 m courses, buttresses 0.64 m, freestanding pillars 0.68 m. Long facade shafts are subdivided in the candidate builder into equal steps of at most 0.48 m with two alternating facade meshes. Their small sinusoidal offsets do not alter equal row cadence within each shaft.
- The stone shader has no explicit brown-stripe mask. The main causes are source assembly, material split, repeated face orientation and the retained broad shoulder. A global exposure/color adjustment cannot repair the assembly.

## Proposed bounded asset contract

Replace the 90 risers, 90 treads and 98 source lips with approximately 90 closed, single-piece stair blocks. Retain the ten supports, 10 level heights, flight footprint, sanctuary landing, cheeks and all portal transforms. Export one Unity-basis world-space mesh and an exact list of source node IDs plus original instance indices to omit. Each row has unequal joint locations with roughly 15-30% width staggering, while total width and the two end positions remain fixed. Approximately one third of noses receive broad 1-5 cm shallow losses; the rest remain quiet and worn. A single neutral stone material covers top and riser, with wetness responding to orientation. This removes the separate bright riser strip at its structural source.

The facade integration should separately vary accumulated row heights and seam starts between neighboring shafts, insert transverse breaks every two to four courses, and use selected shallow local depth offsets. New masonry variants should emphasize upright faces with interrupted local arrises, rather than a continuous sloped perimeter. Existing major silhouettes and useful V8 damage remain protected unless a specific replacement is reviewed in native Unity.

No new visual score is implied by this analysis. Native comparison and movement/performance verification remain required.
