export function previewX(x, frameWidth, reflected) {
  return reflected ? frameWidth - x : x;
}

export function previewBounds(x, boxWidth, frameWidth, reflected) {
  const start = previewX(x, frameWidth, reflected);
  const end = previewX(x + boxWidth, frameWidth, reflected);
  return [Math.max(0, Math.min(start, end)), Math.min(frameWidth - 1, Math.max(start, end))];
}
