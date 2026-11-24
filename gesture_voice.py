from itertools import pairwise

import cv2
import mediapipe as mp

from camera import Camera, camera_args, camera_parser, draw_panel, model_file, run_app, vision_image
from speech import Speech


TITLE = "Gesture Voice Lab"
FINISH = "Speak sequence"
WORDS = {
    "Victory": "Use",
    "Open_Palm": "Technology",
    "Pointing_Up": "For",
    "Thumb_Up": "Help",
    "Thumb_Down": "Not",
    "Closed_Fist": "War",
    "ILoveYou": "I love you",
}
HAND_PATHS = ((0, 1, 2, 3, 4), (0, 5, 6, 7, 8), (5, 9, 10, 11, 12),
              (9, 13, 14, 15, 16), (13, 17, 18, 19, 20), (17, 0))


def read_pose(result):
    hands = len(result.hand_landmarks)
    labels = [group[0].category_name if group and group[0].score >= 0.60 else None
              for group in result.gestures]
    if hands == 2 and labels == ["Open_Palm", "Open_Palm"]:
        return hands, FINISH
    if hands == 1 and labels:
        return hands, WORDS.get(labels[0])
    return hands, None


class PoseHold:
    def __init__(self):
        self.candidate = None
        self.started_at = 0
        self.released_at = None
        self.last_sample = None
        self.locked = False

    def update(self, hands, candidate, now):
        if self.last_sample is not None and now - self.last_sample > 500:
            self.candidate = None
            self.released_at = None
        self.last_sample = now

        if hands:
            self.released_at = None
        else:
            if self.released_at is None:
                self.released_at = now
            if now - self.released_at >= 350:
                self.locked = False

        if self.locked or candidate is None:
            self.candidate = None
            return 0.0, None
        if candidate != self.candidate:
            self.candidate = candidate
            self.started_at = now
        duration = 2000 if candidate == FINISH else 1500
        progress = min(1.0, (now - self.started_at) / duration)
        if progress == 1.0:
            self.locked = True
            return progress, candidate
        return progress, None


def draw_hands(frame, hands):
    height, width = frame.shape[:2]
    for hand in hands:
        points = [(round(x * (width - 1)), round(y * (height - 1))) for x, y in hand]
        for path in HAND_PATHS:
            for start, end in pairwise(path):
                cv2.line(frame, points[start], points[end], (70, 211, 255), 2, cv2.LINE_AA)
        for point in points:
            cv2.circle(frame, point, 3, (255, 255, 255), -1, cv2.LINE_AA)


class GestureSession:
    def __init__(self, speak_each=False):
        self.speak_each = speak_each
        self.words = []
        self.pose_hold = PoseHold()
        self.timestamp = -1

    def __enter__(self):
        vision = mp.tasks.vision
        options = vision.GestureRecognizerOptions(
            base_options=mp.tasks.BaseOptions(model_asset_path=str(model_file("gesture_recognizer.task"))),
            running_mode=vision.RunningMode.VIDEO,
            num_hands=2,
        )
        self.recognizer = vision.GestureRecognizer.create_from_options(options)
        return self

    def __exit__(self, error_type, error, traceback):
        self.recognizer.close()

    def clear(self):
        self.words.clear()

    def utterance(self):
        return " ".join(self.words)

    def process(self, frame, now):
        self.timestamp = max(self.timestamp + 1, int(now * 1000))
        result = self.recognizer.recognize_for_video(vision_image(frame), self.timestamp)
        hands, candidate = read_pose(result)
        progress, accepted = self.pose_hold.update(hands, candidate, self.timestamp)
        added, spoken = None, None
        if accepted == FINISH:
            spoken = self.utterance() or None
        elif accepted:
            self.words.append(accepted)
            added = accepted
            if self.speak_each:
                spoken = accepted

        status = "Show one pose or hold two palms to speak"
        if self.pose_hold.locked:
            status = "Lower your hands briefly to continue"
        elif candidate:
            status = f"Hold {candidate}: {progress:.0%}"
        landmarks = [[[point.x, point.y] for point in hand] for hand in result.hand_landmarks]
        return {"hands": landmarks, "words": list(self.words), "status": status,
                "added": added, "spoken": spoken}


def main():
    parser = camera_parser("Build and speak a sequence from static hand poses.")
    parser.add_argument("--speak-each", action="store_true", help="say each entry as it is added")
    args = camera_args(parser)
    with Camera(args) as camera, Speech() as speech, GestureSession(args.speak_each) as session:
        for frame in camera:
            result = session.process(frame, camera.time)
            if result["added"]:
                print(f"Added: {result['added']}", flush=True)
            if result["spoken"]:
                speech.speak(result["spoken"])
            words = result["words"]
            transcript = ("... " if len(words) > 6 else "") + " ".join(words[-6:])
            draw_hands(frame, result["hands"])
            draw_panel(frame, [result["status"], f"Words: {transcript or '(empty)'}", "S speak | C clear | Q quit"])
            key = camera.show(TITLE, frame)
            if key is None:
                break
            if key == ord("s") and words:
                speech.speak(session.utterance())
            if key == ord("c"):
                session.clear()


if __name__ == "__main__":
    raise SystemExit(run_app(main))
