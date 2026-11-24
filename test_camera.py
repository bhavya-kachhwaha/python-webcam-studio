from types import SimpleNamespace
import unittest
from unittest.mock import patch

from camera import Camera


class CameraWindowTest(unittest.TestCase):
    def test_window_can_open_before_it_becomes_visible(self):
        camera = Camera(SimpleNamespace(video=None, camera=0))
        with (
            patch("camera.cv2.imshow"),
            patch("camera.cv2.waitKey", return_value=-1),
            patch("camera.cv2.getWindowProperty", side_effect=[0, 1, 0]),
        ):
            self.assertEqual(camera.show("Preview", None), -1)
            self.assertEqual(camera.show("Preview", None), -1)
            self.assertIsNone(camera.show("Preview", None))
