import test from 'node:test';
import assert from 'node:assert/strict';
import * as THREE from 'three';
import { attributeComponents } from '../src/export-unity.js';

test('Unity export separates the shared Sprite position and UV buffer', () => {
  const sprite = new THREE.Sprite();
  assert.equal(sprite.geometry.getAttribute('position').isInterleavedBufferAttribute, true);
  assert.deepEqual(attributeComponents(sprite.geometry.getAttribute('position')), [
    -0.5, -0.5, 0, 0.5, -0.5, 0, 0.5, 0.5, 0, -0.5, 0.5, 0,
  ]);
  assert.deepEqual(attributeComponents(sprite.geometry.getAttribute('uv')), [0, 0, 1, 0, 1, 1, 0, 1]);
});

test('Unity export preserves plain and normalized logical attribute values', () => {
  assert.deepEqual(attributeComponents(new THREE.Float32BufferAttribute([1, 2, 3, 4, 5, 6], 3)), [1, 2, 3, 4, 5, 6]);
  assert.deepEqual(attributeComponents(new THREE.Uint8BufferAttribute([0, 255, 0], 3, true)), [0, 1, 0]);
  assert.deepEqual(attributeComponents(undefined), []);
});
