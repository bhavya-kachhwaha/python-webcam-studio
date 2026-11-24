import argparse
import sys
from pathlib import Path
from time import monotonic

import cv2


MODEL_DIR = Path(__file__).resolve().parent / "models"


def camera_parser(description):
    parser = argparse.ArgumentParser(description=description)
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--camera", type=int, default=0, help="camera index (default: 0)")
    source.add_argument("--video", type=Path, metavar="FILE", help="read a local video file")
    return parser


def camera_args(parser):
    args = parser.parse_args()
    if args.camera < 0:
        parser.error("--camera must be zero or greater")
    if args.video is not None and not args.video.is_file():
        parser.error(f"Video file does not exist: {args.video}")
    return args


def fit_preview(frame):
    height, width = frame.shape[:2]
    scale = min(1, 960 / width, 640 / height)
    if scale == 1:
        return frame
    size = (max(1, round(width * scale)), max(1, round(height * scale)))
    return cv2.resize(frame, size, interpolation=cv2.INTER_AREA)


class Camera:
    def __init__(self, args):
        self.video = args.video
        self.source = str(args.video) if args.video is not None else args.camera
        self.time = 0.0
        self.frame_index = 0
        self.window_seen = False

    def __enter__(self):
        self.capture = cv2.VideoCapture(self.source)
        if not self.capture.isOpened():
            self.capture.release()
            raise RuntimeError(f"Cannot open {self.source!r}. Check the video path or camera permissions and index.")
        fps = self.capture.get(cv2.CAP_PROP_FPS) if self.video is not None else 0
        self.frame_period = 1 / fps if fps > 0 else 1 / 30
        self.started_at = monotonic()
        return self

    def __iter__(self):
        while True:
            ok, frame = self.capture.read()
            if not ok:
                if self.video is not None and self.frame_index > 0:
                    return
                raise RuntimeError(f"Could not read a frame from {self.source!r}.")
            now = monotonic() - self.started_at
            self.time = self.frame_index * self.frame_period if self.video is not None else now
            self.frame_index += 1
            yield fit_preview(frame)

    def show(self, title, frame):
        cv2.imshow(title, frame)
        delay = 1
        if self.video is not None:
            remaining = self.time + self.frame_period - (monotonic() - self.started_at)
            delay = max(1, round(remaining * 1000))
        key = cv2.waitKey(delay)
        if key in (27, ord("q")):
            return None
        visible = cv2.getWindowProperty(title, cv2.WND_PROP_VISIBLE) >= 1
        if self.window_seen and not visible:
            return None
        self.window_seen = visible
        return key

    def __exit__(self, error_type, error, traceback):
        self.capture.release()
        cv2.destroyAllWindows()


def model_file(name):
    path = MODEL_DIR / name
    if not path.is_file():
        raise RuntimeError(f"Missing model {name}. Run python download_models.py from the project folder.")
    return path


def vision_image(frame):
    import mediapipe as mp

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    return mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)


def draw_panel(frame, lines):
    width = frame.shape[1]
    cv2.rectangle(frame, (0, 0), (width - 1, 10 + 23 * len(lines)), (26, 23, 20), cv2.FILLED)
    for row, line in enumerate(lines):
        font = cv2.FONT_HERSHEY_SIMPLEX
        text_width = cv2.getTextSize(line, font, 0.55, 1)[0][0]
        scale = 0.55 * min(1, max(1, width - 24) / max(1, text_width))
        cv2.putText(frame, line, (12, 23 + row * 23), font, scale, (243, 243, 238), 1, cv2.LINE_AA)


def run_app(main):
    try:
        return main() or 0
    except KeyboardInterrupt:
        return 0
    except (OSError, RuntimeError) as error:
        print(error, file=sys.stderr)
        return 1
