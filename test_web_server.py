import unittest

import cv2
import numpy as np
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from web_server import MAX_MESSAGE, OBJECTS, app, decode_frame


ORIGIN = {"origin": "http://testserver"}
URL = "/ws/" + OBJECTS


def jpeg(frame):
    ok, image = cv2.imencode(".jpg", frame)
    assert ok
    return image.tobytes()


class BrowserAPI(unittest.TestCase):
    def test_decode_accepts_jpeg_in_bgr_and_checks_size(self):
        blue = np.full((80, 100, 3), (220, 0, 0), dtype=np.uint8)
        decoded = decode_frame(jpeg(blue))
        self.assertEqual(decoded.shape, (80, 100, 3))
        self.assertGreater(int(decoded[40, 50, 0]), 215)
        with self.assertRaises(ValueError):
            decode_frame(jpeg(np.zeros((481, 640, 3), dtype=np.uint8)))
        with self.assertRaises(ValueError):
            decode_frame(bytes(MAX_MESSAGE + 1))

    def test_socket_motion_sessions_are_isolated_and_recover_from_bad_input(self):
        still = np.zeros((200, 320, 3), dtype=np.uint8)
        changed = still.copy()
        changed[60:130, 80:170] = 255
        with TestClient(app) as client, client.websocket_connect(URL, headers=ORIGIN) as first:
            self.assertEqual(first.receive_json(), {"type": "ready"})
            first.send_json({"type": "settings", "mode": "motion", "show_mask": True})
            first.send_bytes(b"broken jpg")
            self.assertFalse(first.receive_json()["fatal"])
            first.send_bytes(jpeg(still))
            self.assertEqual(first.receive_json()["motion"], [])

            with client.websocket_connect(URL, headers=ORIGIN) as second:
                self.assertEqual(second.receive_json()["type"], "ready")
                second.send_json({"type": "settings", "mode": "motion"})
                second.send_bytes(jpeg(changed))
                self.assertEqual(second.receive_json()["motion"], [])

                first.send_bytes(jpeg(changed))
                result = first.receive_json()
                self.assertEqual((result["width"], result["height"]), (320, 200))
                self.assertEqual(len(result["motion"]), 1)
                self.assertTrue(result["mask"].startswith("data:image/png;base64,"))

    def test_socket_rejects_another_origin(self):
        with TestClient(app) as client, self.assertRaises(WebSocketDisconnect) as rejected:
            with client.websocket_connect(URL, headers={"origin": "https://another.example"}):
                self.fail("Connection should have been rejected")
        self.assertEqual(rejected.exception.code, 1008)
