import unittest
from unittest.mock import patch

import numpy as np

from motion_detector import ObjectMotionSession, detect_motion, prepare_frame
from object_detection import Detection


class MotionDetectorTest(unittest.TestCase):
    def test_still_noise_and_motion(self):
        blank = np.zeros((160, 240, 3), dtype=np.uint8)
        changed = blank.copy()
        changed[40:100, 70:150] = 255
        changed[12:14, 12:14] = 255

        previous = prepare_frame(blank)
        current = prepare_frame(changed)

        mask, boxes = detect_motion(previous, previous, threshold=20, min_area=200)
        self.assertFalse(mask.any())
        self.assertEqual(boxes, [])

        mask, boxes = detect_motion(previous, current, threshold=20, min_area=200)
        self.assertEqual(len(boxes), 1)
        x, y, width, height = boxes[0]
        self.assertTrue(66 <= x <= 70 and 36 <= y <= 40)
        self.assertTrue(80 <= width <= 88 and 60 <= height <= 68)
        self.assertEqual(mask[70, 110], 255)
        self.assertEqual(mask[12, 12], 255)

        mask, boxes = detect_motion(current, current, threshold=20, min_area=200)
        self.assertFalse(mask.any())
        self.assertEqual(boxes, [])

    def test_single_session_can_switch_between_motion_and_objects(self):
        blank = np.zeros((160, 240, 3), dtype=np.uint8)
        changed = blank.copy()
        changed[40:100, 70:150] = 255
        prediction = Detection("person", 0.9, (10, 20, 30, 40))
        with (
            patch("motion_detector.create_detector") as create,
            patch("motion_detector.infer_objects", return_value=[prediction]),
            ObjectMotionSession(mode="motion", show_mask=True) as session,
        ):
            self.assertEqual(session.process(blank, 0.0)["motion"], [])
            self.assertEqual(len(session.process(changed, 0.2)["motion"]), 1)
            create.assert_not_called()
            session.mode = "objects"
            self.assertIsNone(session.process(blank, 0.4)["mask"])
            self.assertEqual(session.process(blank, 0.6)["objects"], [
                {"label": "person", "score": 0.9, "box": [10, 20, 30, 40]},
            ])
            session.mode = "both"
            self.assertEqual(session.process(changed, 0.8)["motion"], [])
        create.return_value.close.assert_called_once_with()
