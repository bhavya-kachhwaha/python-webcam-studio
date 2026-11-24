from dataclasses import dataclass

import cv2

from camera import model_file, vision_image


COLORS = ((255, 196, 92), (220, 141, 255), (90, 213, 255), (156, 178, 255))
TRACK_HOLD = 0.4
INPUT_SIZE = 448


@dataclass
class Detection:
    name: str
    score: float
    box: tuple[int, int, int, int]


@dataclass
class Track:
    detection: Detection
    last_seen: float
    hits: int = 1


def intersection_over_union(first, second):
    x, y, width, height = first
    other_x, other_y, other_width, other_height = second
    overlap_width = max(0, min(x + width, other_x + other_width) - max(x, other_x))
    overlap_height = max(0, min(y + height, other_y + other_height) - max(y, other_y))
    intersection = overlap_width * overlap_height
    union = width * height + other_width * other_height - intersection
    return intersection / union if union else 0.0


class ObjectTracks:
    def __init__(self):
        self.tracks = []

    def update(self, detections, now):
        available = [track for track in self.tracks if now - track.last_seen <= TRACK_HOLD]
        updated = []
        for detection in sorted(detections, key=lambda item: item.score, reverse=True):
            candidates = (
                (intersection_over_union(detection.box, track.detection.box), index)
                for index, track in enumerate(available)
                if track.detection.name == detection.name
            )
            overlap, index = max(candidates, default=(0, -1))
            if overlap < 0.25:
                updated.append(Track(detection, now))
                continue
            prior = available.pop(index)
            smoothed = tuple(round(old * 0.35 + new * 0.65)
                             for old, new in zip(prior.detection.box, detection.box))
            tracked = Detection(detection.name, detection.score, smoothed)
            updated.append(Track(tracked, now, prior.hits + 1))
        self.tracks = updated + [track for track in available if track.hits >= 2]

    def visible(self, now):
        return [track.detection for track in self.tracks
                if track.hits >= 2 and now - track.last_seen <= TRACK_HOLD]


def create_detector(confidence):
    import mediapipe as mp

    asset = mp.tasks.BaseOptions(model_asset_path=str(model_file("efficientdet_lite2.tflite")))
    options = mp.tasks.vision.ObjectDetectorOptions(base_options=asset, score_threshold=confidence, max_results=12)
    return mp.tasks.vision.ObjectDetector.create_from_options(options)


def fit_for_model(frame):
    height, width = frame.shape[:2]
    scale = INPUT_SIZE / max(width, height)
    scaled_width = max(1, round(width * scale))
    scaled_height = max(1, round(height * scale))
    left = (INPUT_SIZE - scaled_width) // 2
    top = (INPUT_SIZE - scaled_height) // 2
    interpolation = cv2.INTER_AREA if scale < 1 else cv2.INTER_LINEAR
    resized = cv2.resize(frame, (scaled_width, scaled_height), interpolation=interpolation)
    padded = cv2.copyMakeBorder(
        resized, top, INPUT_SIZE - top - scaled_height, left, INPUT_SIZE - left - scaled_width,
        cv2.BORDER_CONSTANT, value=(128, 128, 128),
    )
    return padded, left, top, width / scaled_width, height / scaled_height


def infer_objects(detector, frame):
    padded, left, top, scale_x, scale_y = fit_for_model(frame)
    result = detector.detect(vision_image(padded))
    detections = []
    for item in result.detections:
        category = item.categories[0]
        bounds = item.bounding_box
        box = (
            round((bounds.origin_x - left) * scale_x), round((bounds.origin_y - top) * scale_y),
            round(bounds.width * scale_x), round(bounds.height * scale_y),
        )
        detections.append(Detection(category.category_name, category.score, box))
    return detections


def draw_objects(frame, detections):
    height, width = frame.shape[:2]
    font = cv2.FONT_HERSHEY_SIMPLEX
    for detection in detections:
        x, y, box_width, box_height = detection.box
        left, top = max(0, x), max(0, y)
        right, bottom = min(width - 1, x + box_width - 1), min(height - 1, y + box_height - 1)
        if left >= right or top >= bottom:
            continue
        color = COLORS[sum(map(ord, detection.name)) % len(COLORS)]
        label = f"{detection.name} {detection.score:.0%}"
        label_width = cv2.getTextSize(label, font, 0.48, 1)[0][0] + 10
        label_x = min(left, max(0, width - label_width))
        label_y = top - 22 if top >= 22 else top
        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        cv2.rectangle(frame, (label_x, label_y), (label_x + label_width, label_y + 22), color, cv2.FILLED)
        cv2.putText(frame, label, (label_x + 5, label_y + 15), font, 0.48, (24, 22, 20), 1, cv2.LINE_AA)
