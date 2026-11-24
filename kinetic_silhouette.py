import cv2
import mediapipe as mp
import numpy as np

from camera import Camera, camera_args, camera_parser, draw_panel, model_file, run_app, vision_image


TITLE = "Kinetic Silhouette"
WIDTH, HEIGHT = 960, 540
BLUE = (238, 211, 113)
VIOLET = (244, 161, 185)
GOLD = (100, 201, 255)
MOTION_KERNEL = np.ones((3, 3), dtype=np.uint8)


def make_landscape():
    sky = np.linspace((24, 12, 13), (74, 38, 52), HEIGHT, dtype=np.uint8)
    scene = np.repeat(sky[:, None, :], WIDTH, axis=1)
    random = np.random.default_rng(18)
    for x, y in random.integers((0, 55), (WIDTH, 355), size=(110, 2)):
        cv2.circle(scene, (int(x), int(y)), 1, (182, 169, 191), -1, cv2.LINE_AA)

    moon = np.zeros((HEIGHT, WIDTH), dtype=np.uint8)
    cv2.circle(moon, (159, 156), 29, 255, -1)
    cv2.circle(moon, (170, 143), 25, 0, -1)
    scene[moon != 0] = (236, 215, 249)

    ridge_x = np.arange(0, WIDTH + 1, 24)
    for level, shift, depth, color in [(347, 0, 23, (57, 27, 38)), (401, 1.7, 18, (33, 21, 25))]:
        ridge_y = level + depth * np.sin(ridge_x / 93 + shift)
        ridge = np.column_stack((ridge_x, ridge_y)).astype(np.int32)
        hill = np.vstack((ridge, [[WIDTH, HEIGHT], [0, HEIGHT]])).astype(np.int32)
        cv2.fillPoly(scene, [hill], color, cv2.LINE_AA)

    for x, y in random.integers((0, 425), (WIDTH, HEIGHT + 8), size=(270, 2)):
        length = int(random.integers(4, 14))
        cv2.line(scene, (int(x), int(y)), (int(x) + 3, int(y) - length), (66, 44, 60), 1, cv2.LINE_AA)
    return scene


def small_frame(frame):
    height, width = frame.shape[:2]
    scale = min(1, 320 / width, 180 / height)
    size = max(1, round(width * scale)), max(1, round(height * scale))
    return cv2.resize(frame, size, interpolation=cv2.INTER_AREA)


def person_mask(segmenter, frame, milliseconds, previous):
    result = segmenter.segment_for_video(vision_image(frame), milliseconds)
    confidence = result.confidence_masks[-1].numpy_view().reshape(frame.shape[:2])
    mask = confidence >= 0.65
    if previous is not None and previous.shape == mask.shape:
        mask |= (confidence >= 0.52) & previous
    return mask


def body_motion(previous_gray, previous_person, gray, person):
    if previous_gray is None or previous_gray.shape != gray.shape:
        return np.zeros_like(person)

    delta = gray.astype(np.int16) - previous_gray
    brighter = np.count_nonzero(delta > 8)
    darker = np.count_nonzero(delta < -8)
    if max(brighter, darker) > delta.size * 0.75:
        delta -= int(np.median(delta))

    changed = (np.abs(delta) >= 20) | ~previous_person
    candidate = (person & changed).astype(np.uint8)
    return cv2.morphologyEx(candidate, cv2.MORPH_OPEN, MOTION_KERNEL).astype(bool)


def draw_particles(landscape, person, moving):
    image = landscape.copy()
    height, width = person.shape
    y, x = np.nonzero(person[::2, ::2])
    y, x = y * 2, x * 2
    scale = min((WIDTH - 100) / width, (HEIGHT - 87) / height)
    output_x = np.rint((x - width / 2) * scale + WIDTH / 2).astype(int)
    output_y = np.rint((y - height) * scale + HEIGHT - 18).astype(int)
    colors = np.tile(BLUE, (x.size, 1))
    colors[(x + y) % 8 == 0] = VIOLET
    colors[moving[y, x]] = GOLD
    image[output_y, output_x] = colors
    image[output_y, output_x + 1] = colors
    image[output_y + 1, output_x] = colors
    return image


def draw_mask(person, moving):
    colors = np.zeros((*person.shape, 3), dtype=np.uint8)
    colors[person] = BLUE
    colors[moving] = GOLD
    height, width = person.shape
    scale = min((WIDTH - 100) / width, (HEIGHT - 87) / height)
    size = round(width * scale), round(height * scale)
    enlarged = cv2.resize(colors, size, interpolation=cv2.INTER_NEAREST)
    image = np.full((HEIGHT, WIDTH, 3), (24, 12, 13), dtype=np.uint8)
    left, top = (WIDTH - size[0]) // 2, HEIGHT - 18 - size[1]
    image[top:top + size[1], left:left + size[0]] = enlarged
    return image


class SilhouetteSession:
    def __init__(self):
        self.landscape = make_landscape()
        self.previous_gray = None
        self.previous_person = None
        self.last_timestamp = -1
        self.view_mask = False
        self.mirror = True

    def __enter__(self):
        model = str(model_file("selfie_segmenter_landscape.tflite"))
        options = mp.tasks.vision.ImageSegmenterOptions(
            base_options=mp.tasks.BaseOptions(model_asset_path=model),
            running_mode=mp.tasks.vision.RunningMode.VIDEO,
            output_confidence_masks=True,
        )
        self.segmenter = mp.tasks.vision.ImageSegmenter.create_from_options(options)
        return self

    def process(self, frame, now):
        small = small_frame(frame)
        gray = cv2.GaussianBlur(cv2.cvtColor(small, cv2.COLOR_BGR2GRAY), (5, 5), 0)
        self.last_timestamp = max(self.last_timestamp + 1, int(now * 1000))
        person = person_mask(self.segmenter, small, self.last_timestamp, self.previous_person)
        moving = body_motion(self.previous_gray, self.previous_person, gray, person)
        self.previous_gray, self.previous_person = gray, person

        if self.mirror:
            person, moving = person[:, ::-1], moving[:, ::-1]
        art = draw_mask(person, moving) if self.view_mask else draw_particles(self.landscape, person, moving)
        visible = int(np.count_nonzero(person))
        motion = 100 * int(np.count_nonzero(moving)) / visible if visible else 0.0
        return {"art": art, "motion_percent": motion, "body_present": visible > 0}

    def __exit__(self, error_type, error, traceback):
        self.segmenter.close()


def main():
    parser = camera_parser("Turn a webcam silhouette into motion-reactive particles.")
    args = camera_args(parser)
    with SilhouetteSession() as session, Camera(args) as camera:
        for frame in camera:
            result = session.process(frame, camera.time)
            image = result["art"]
            motion = result["motion_percent"]
            status = f"Body motion: {motion:.1f}%" if result["body_present"] else "Step into camera view"
            view = "Mask view" if session.view_mask else TITLE
            draw_panel(image, [f"{view} | {status}", "Blue: person    Gold: movement    M: switch view    Q: quit"])
            key = camera.show(TITLE, image)
            if key is None:
                break
            if key == ord("m"):
                session.view_mask = not session.view_mask


if __name__ == "__main__":
    raise SystemExit(run_app(main))
