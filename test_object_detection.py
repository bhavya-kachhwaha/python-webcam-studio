import unittest

import numpy as np

from object_detection import Detection, ObjectTracks, fit_for_model, intersection_over_union


class ObjectTracksTest(unittest.TestCase):
    def test_confirm_smooth_and_expire(self):
        tracks = ObjectTracks()
        cat = Detection("cat", 0.9, (10, 20, 80, 60))
        dog = Detection("dog", 0.8, (100, 20, 80, 60))
        tracks.update([cat, dog], 0.0)
        self.assertEqual(tracks.visible(0.0), [])

        tracks.update([Detection("cat", 0.93, (20, 20, 80, 60))], 0.2)
        self.assertEqual(tracks.visible(0.2), [Detection("cat", 0.93, (16, 20, 80, 60))])
        tracks.update([], 0.4)
        self.assertEqual(len(tracks.visible(0.5)), 1)
        self.assertEqual(tracks.visible(0.7), [])

    def test_same_name_can_have_distinct_boxes(self):
        tracks = ObjectTracks()
        first = Detection("cat", 0.9, (10, 20, 80, 60))
        second = Detection("cat", 0.8, (100, 20, 80, 60))
        self.assertEqual(intersection_over_union(first.box, second.box), 0.0)
        tracks.update([first, second], 0.0)
        tracks.update([second, first], 0.2)
        self.assertEqual(tracks.visible(0.2), [first, second])

    def test_letterbox_preserves_wide_frame_geometry(self):
        image = np.full((240, 480, 3), 220, dtype=np.uint8)
        padded, left, top, sx, sy = fit_for_model(image)
        self.assertEqual(padded.shape, (448, 448, 3))
        self.assertEqual((left, top), (0, 112))
        self.assertEqual((448 * sx, 224 * sy), (480, 240))
        self.assertEqual(int(padded[0, 0, 0]), 128)
        self.assertEqual(int(padded[112, 0, 0]), 220)
