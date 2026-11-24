from types import SimpleNamespace
import unittest
from unittest.mock import patch

from gesture_voice import FINISH, GestureSession, PoseHold, read_pose


def result(*labels, score=0.95):
    return SimpleNamespace(
        hand_landmarks=[[] for label in labels],
        gestures=[[SimpleNamespace(category_name=label, score=score)] for label in labels],
    )


class GestureVoiceTest(unittest.TestCase):
    def test_pose_mapping_and_confidence(self):
        self.assertEqual(read_pose(result("Thumb_Up")), (1, "Help"))
        self.assertEqual(read_pose(result("Thumb_Up", score=0.30)), (1, None))
        self.assertEqual(read_pose(result("Open_Palm", "Open_Palm")), (2, FINISH))
        self.assertEqual(read_pose(result("Open_Palm", "Victory")), (2, None))

    def test_word_acceptance_and_release(self):
        hold = PoseHold()
        for timestamp in range(0, 1500, 250):
            self.assertIsNone(hold.update(1, "Help", timestamp)[1])
        self.assertEqual(hold.update(1, "Help", 1500), (1.0, "Help"))
        self.assertEqual(hold.update(1, "Help", 1750), (0.0, None))
        hold.update(0, None, 1900)
        hold.update(1, "Help", 2000)
        self.assertTrue(hold.locked)
        hold.update(0, None, 2100)
        hold.update(0, None, 2450)
        self.assertFalse(hold.locked)
        self.assertEqual(hold.update(1, "Help", 2500), (0.0, None))

    def test_dropped_frames_reset_progress(self):
        hold = PoseHold()
        hold.update(2, FINISH, 0)
        self.assertGreater(hold.update(2, FINISH, 400)[0], 0.0)
        self.assertEqual(hold.update(2, FINISH, 2800), (0.0, None))
        for timestamp in range(3100, 4800, 300):
            self.assertIsNone(hold.update(2, FINISH, timestamp)[1])
        self.assertEqual(hold.update(2, FINISH, 4800), (1.0, FINISH))

    def test_session_reports_landmarks_and_speech_once_per_hold(self):
        prediction = result("Thumb_Up")
        prediction.hand_landmarks = [[SimpleNamespace(x=0.25, y=0.75)]]
        with (
            patch("gesture_voice.model_file", return_value="gesture_recognizer.task"),
            patch("gesture_voice.vision_image"),
            patch("gesture_voice.mp.tasks.vision.GestureRecognizer.create_from_options") as create,
            GestureSession(speak_each=True) as session,
        ):
            create.return_value.recognize_for_video.return_value = prediction
            for step in range(6):
                self.assertEqual(session.process(None, step / 4)["words"], [])
            accepted = session.process(None, 1.5)
            self.assertEqual(accepted["hands"], [[[0.25, 0.75]]])
            self.assertEqual((accepted["words"], accepted["spoken"]), (["Help"], "Help"))
            self.assertIsNone(session.process(None, 1.75)["spoken"])
            self.assertEqual(session.utterance(), "Help")
            session.clear()
            self.assertEqual(session.utterance(), "")
        create.return_value.close.assert_called_once_with()
