import unittest
from unittest.mock import Mock, patch

import numpy as np

from kinetic_silhouette import BLUE, GOLD, SilhouetteSession, body_motion, draw_mask, draw_particles, make_landscape


class SilhouetteTest(unittest.TestCase):
    def test_motion_stays_in_person_and_ignores_uniform_brightness_shift(self):
        previous = np.full((40, 60), 75, dtype=np.uint8)
        person = np.zeros(previous.shape, dtype=bool)
        person[10:30, 10:30] = True
        current = previous + 30
        current[5:15, 15:25] = 180
        current[31:39, 45:55] = 180

        moving = body_motion(previous, person, current, person)
        self.assertFalse(moving[3, 3])
        self.assertFalse(moving[20, 20])
        self.assertFalse(moving[34, 50])
        self.assertTrue(moving[12, 20])
        self.assertFalse(body_motion(None, None, current, person).any())

    def test_new_foreground_glows_and_both_views_show_motion(self):
        gray = np.full((50, 60), 80, dtype=np.uint8)
        before = np.zeros(gray.shape, dtype=bool)
        before[12:34, 12:24] = True
        person = before.copy()
        person[12:34, 24:36] = True

        moving = body_motion(gray, before, gray, person)
        self.assertTrue(moving[18, 30])
        self.assertFalse(moving[18, 18])
        for image in (draw_particles(make_landscape(), person, moving), draw_mask(person, moving)):
            self.assertTrue(np.any(np.all(image == BLUE, axis=-1)))
            self.assertTrue(np.any(np.all(image == GOLD, axis=-1)))

    def test_shared_session_owns_history_and_closes_model(self):
        frame = np.full((50, 60, 3), 80, dtype=np.uint8)
        changed = frame.copy()
        changed[12:34, 12:24] = 180
        confidence = Mock()
        confidence.numpy_view.return_value = np.ones(frame.shape[:2], dtype=np.float32)
        segmenter = Mock()
        segmenter.segment_for_video.return_value.confidence_masks = [confidence]

        with patch("kinetic_silhouette.model_file", return_value="model.tflite"), patch(
            "kinetic_silhouette.mp.tasks.vision.ImageSegmenter.create_from_options", return_value=segmenter
        ):
            with SilhouetteSession() as session:
                first = session.process(frame, 0.0)
                session.view_mask = True
                next_frame = session.process(changed, 0.0)
            with SilhouetteSession() as fresh_session:
                fresh = fresh_session.process(changed, 0.0)

        self.assertIs(first["body_present"], True)
        self.assertEqual(first["motion_percent"], 0.0)
        self.assertGreater(next_frame["motion_percent"], 0.0)
        self.assertGreater(np.all(next_frame["art"] == GOLD, axis=-1).sum(), 100)
        self.assertEqual(fresh["motion_percent"], 0.0)
        timestamps = [call.args[1] for call in segmenter.segment_for_video.call_args_list]
        self.assertEqual(timestamps, [0, 1, 0])
        self.assertEqual(segmenter.close.call_count, 2)

    def test_mirror_reflects_subject_without_counting_it_as_motion(self):
        frame = np.full((50, 60, 3), 80, dtype=np.uint8)
        person = np.zeros(frame.shape[:2], dtype=bool)
        person[12:34, 5:18] = True
        session = SilhouetteSession()
        session.segmenter = Mock()
        with patch("kinetic_silhouette.person_mask", return_value=person):
            reflected = session.process(frame, 0.0)
            session.mirror = False
            original = session.process(frame, 1.0)

        reflected_x = np.nonzero(np.all(reflected["art"] == BLUE, axis=-1))[1]
        original_x = np.nonzero(np.all(original["art"] == BLUE, axis=-1))[1]
        center = reflected["art"].shape[1] / 2
        self.assertGreater(reflected_x.mean(), center)
        self.assertLess(original_x.mean(), center)
        self.assertEqual(original["motion_percent"], 0.0)
        np.testing.assert_array_equal(reflected["art"][:, :185], original["art"][:, :185])
