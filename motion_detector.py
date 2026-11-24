import cv2

from camera import Camera, camera_args, camera_parser, run_app
from object_detection import Detection, ObjectTracks, create_detector, draw_objects, infer_objects


PREVIEW = "Object Motion Lab"
MASK_WINDOW = "Motion mask"
BOX_COLOR = (110, 255, 170)
KERNEL = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))


def prepare_frame(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return cv2.GaussianBlur(gray, (5, 5), 0)


def detect_motion(previous, current, threshold, min_area):
    difference = cv2.absdiff(previous, current)
    _, mask = cv2.threshold(difference, threshold, 255, cv2.THRESH_BINARY)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, KERNEL)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    boxes = []
    for contour in contours:
        if cv2.contourArea(contour) >= min_area:
            boxes.append(cv2.boundingRect(contour))
    return mask, boxes


def draw_motion(frame, boxes):
    for x, y, width, height in boxes:
        cv2.rectangle(frame, (x, y), (x + width - 1, y + height - 1), BOX_COLOR, 2)
        label_y = y - 6 if y >= 22 else y + 18
        cv2.putText(
            frame, "Motion", (x + 3, label_y), cv2.FONT_HERSHEY_SIMPLEX,
            0.5, BOX_COLOR, 2, cv2.LINE_AA,
        )


class ObjectMotionSession:
    def __init__(self, mode="both", confidence=0.4, threshold=20, min_area=200, show_mask=False):
        self.mode = mode
        self.confidence = confidence
        self.threshold = threshold
        self.min_area = min_area
        self.show_mask = show_mask
        self.detector = None
        self.tracks = ObjectTracks()
        self.next_inference = 0.0
        self.shape = None
        self.previous = None

    def __enter__(self):
        return self

    def __exit__(self, error_type, error, traceback):
        if self.detector is not None:
            self.detector.close()

    def process(self, frame, now):
        shape = frame.shape[:2]
        if shape != self.shape or self.mode == "motion":
            self.tracks.tracks.clear()
            self.next_inference = now
        self.shape = shape

        objects = []
        if self.mode != "motion":
            if self.detector is None:
                self.detector = create_detector(self.confidence)
            if now >= self.next_inference:
                self.tracks.update(infer_objects(self.detector, frame), now)
                self.next_inference = now + 0.17
            objects = [
                {"label": detection.name, "score": detection.score, "box": list(detection.box)}
                for detection in self.tracks.visible(now)
            ]

        mask, boxes = None, []
        if self.mode == "objects":
            self.previous = None
        else:
            gray = prepare_frame(frame)
            previous = self.previous
            if previous is None or previous.shape != gray.shape:
                previous = gray
            mask, boxes = detect_motion(previous, gray, self.threshold, self.min_area)
            self.previous = gray
        return {"objects": objects, "motion": [list(box) for box in boxes],
                "mask": mask if self.show_mask else None}


def parse_args():
    parser = camera_parser("Show named objects and motion regions on a live camera or video.")
    parser.add_argument("--mode", choices=("both", "objects", "motion"), default="both")
    parser.add_argument("--confidence", type=float, default=0.4, help="minimum object confidence (default: 0.4)")
    parser.add_argument("--threshold", type=int, default=20, help="minimum brightness change (default: 20)")
    parser.add_argument("--min-area", type=int, default=200, help="minimum contour area in pixels² (default: 200)")
    parser.add_argument("--show-mask", action="store_true", help="open a window for the binary motion mask")
    args = camera_args(parser)
    if not 0 < args.confidence <= 1:
        parser.error("--confidence must be greater than zero and up to one")
    if not 0 <= args.threshold < 255:
        parser.error("--threshold must be between 0 and 254")
    if args.min_area < 1:
        parser.error("--min-area must be positive")
    if args.mode == "objects" and args.show_mask:
        parser.error("--show-mask needs motion or both mode")
    return args


def main():
    args = parse_args()
    with Camera(args) as camera, ObjectMotionSession(
        mode=args.mode, confidence=args.confidence, threshold=args.threshold,
        min_area=args.min_area, show_mask=args.show_mask,
    ) as session:
        for frame in camera:
            result = session.process(frame, camera.time)
            draw_motion(frame, result["motion"])
            if result["mask"] is not None:
                cv2.imshow(MASK_WINDOW, result["mask"])
            draw_objects(frame, (Detection(item["label"], item["score"], tuple(item["box"]))
                                 for item in result["objects"]))
            if camera.show(PREVIEW, frame) is None:
                break


if __name__ == "__main__":
    raise SystemExit(run_app(main))
