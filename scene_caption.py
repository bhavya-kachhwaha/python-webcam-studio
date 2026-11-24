from concurrent.futures import ThreadPoolExecutor
import sys
from textwrap import wrap

import cv2
import numpy as np

from camera import Camera, camera_args, camera_parser, draw_panel, model_file, run_app
from speech import Speech


TITLE = "Scene Caption Camera"
END_OF_TEXT = 50256
PAST_NAMES = tuple(
    f"past_key_values.{layer}.{kind}"
    for layer in range(12)
    for kind in ("key", "value")
)
OUTPUT_NAMES = ["logits", *(name.replace("past_key_values.", "present.") for name in PAST_NAMES)]


def image_tensor(frame):
    resized = cv2.resize(frame, (224, 224), interpolation=cv2.INTER_LINEAR)
    rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB).astype(np.float32)
    normalized = rgb / 127.5 - 1.0
    return np.ascontiguousarray(normalized.transpose(2, 0, 1)[None])


def generate_tokens(decoder, image_features):
    empty_cache = np.empty((1, 12, 0, 64), dtype=np.float32)
    inputs = dict.fromkeys(PAST_NAMES, empty_cache)
    inputs["encoder_hidden_states"] = image_features
    inputs["use_cache_branch"] = np.array([False], dtype=np.bool_)
    token = END_OF_TEXT
    sequence = []
    for _ in range(30):
        inputs["input_ids"] = np.array([[token]], dtype=np.int64)
        logits, *cache = decoder.run(OUTPUT_NAMES, inputs)
        token = int(logits[0, -1].argmax())
        if token == END_OF_TEXT:
            break
        sequence.append(token)
        inputs.update(zip(PAST_NAMES, cache))
        inputs["use_cache_branch"][0] = True
    return sequence


def load_model():
    import onnxruntime as ort
    from tokenizers import Tokenizer
    ort.disable_telemetry_events()
    encoder_path = model_file("caption/onnx/encoder_model_quantized.onnx")
    decoder_path = model_file("caption/onnx/decoder_model_merged_quantized.onnx")
    tokenizer_path = model_file("caption/tokenizer.json")
    options = ort.SessionOptions()
    options.intra_op_num_threads = 4
    providers = ["CPUExecutionProvider"]
    encoder = ort.InferenceSession(str(encoder_path), sess_options=options, providers=providers)
    decoder = ort.InferenceSession(str(decoder_path), sess_options=options, providers=providers)
    tokenizer = Tokenizer.from_file(str(tokenizer_path))
    return encoder, decoder, tokenizer


class Captioner:
    def __init__(self):
        self.model = None

    def describe(self, frame):
        if self.model is None:
            self.model = load_model()
        encoder, decoder, tokenizer = self.model
        pixels = image_tensor(frame)
        features, = encoder.run(["last_hidden_state"], {"pixel_values": pixels})
        sequence = generate_tokens(decoder, features)
        caption = tokenizer.decode(sequence, skip_special_tokens=True).strip()
        if not caption:
            raise RuntimeError("The model returned an empty caption.")
        return caption


def main():
    parser = camera_parser("Describe and speak a camera or video frame.")
    parser.add_argument("--auto", action="store_true", help="periodically describe the scene")
    args = camera_args(parser)
    captioner = Captioner()
    auto = args.auto
    next_caption = 0.0
    request = None
    caption = ""
    status = "Press C to describe a frame."

    with ThreadPoolExecutor(max_workers=1) as worker, Camera(args) as camera, Speech() as speech:
        for frame in camera:
            if request is not None and request.done():
                try:
                    caption = request.result()
                    print(caption, flush=True)
                    status = "Caption ready."
                except Exception as error:
                    print(f"Caption unavailable: {error}", file=sys.stderr)
                    status = "Caption unavailable. Check the terminal, then press C."
                    auto = False
                request = None
                next_caption = camera.time + 4.0

            if auto and request is None and camera.time >= next_caption:
                request = worker.submit(captioner.describe, frame.copy())

            preview = frame.copy()
            auto_status = "on" if auto else "off"
            message = "Describing frame..." if request is not None else status
            controls = f"C describe   S speak   A auto {auto_status}   Q quit"
            draw_panel(preview, [TITLE, controls, message, *wrap(caption, width=64)])
            key = camera.show(TITLE, preview)
            if key is None:
                break
            if key == ord("c") and request is None:
                request = worker.submit(captioner.describe, frame.copy())
            elif key == ord("a"):
                auto = not auto
                next_caption = camera.time
            elif key == ord("s") and caption:
                try:
                    speech.speak(caption)
                except (OSError, RuntimeError) as error:
                    print(error, file=sys.stderr)
                    status = "Speech unavailable. Check the terminal."


if __name__ == "__main__":
    raise SystemExit(run_app(main))
