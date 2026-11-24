import assert from "node:assert/strict";
import { test } from "node:test";
import { previewBounds, previewX } from "./web/mirror.mjs";

test("mirror x coordinates for hand landmarks and preserve x when off", () => {
  assert.equal(previewX(64, 640, true), 576);
  assert.equal(previewX(64, 640, false), 64);
});

test("mirror both edges of a box and preserve horizontal width", () => {
  assert.deepEqual(previewBounds(64, 128, 640, true), [448, 576]);
  assert.deepEqual(previewBounds(64, 128, 640, false), [64, 192]);
});

test("clip edges that cross the camera frame", () => {
  assert.deepEqual(previewBounds(-16, 80, 640, true), [576, 639]);
  assert.deepEqual(previewBounds(-16, 80, 640, false), [0, 64]);
});
