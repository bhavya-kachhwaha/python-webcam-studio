import argparse
import hashlib
from pathlib import Path
from tempfile import NamedTemporaryFile
from urllib.request import urlopen

from camera import MODEL_DIR, run_app


GOOGLE = "https://storage.googleapis.com/mediapipe-models/"
CAPTIONS = "https://huggingface.co/Xenova/vit-gpt2-image-captioning/resolve/077550ae0729f9af280c9d885ea9b0380fc8e815/"
MODELS = {
    "objects": (
        ("efficientdet_lite2.tflite", GOOGLE + "object_detector/efficientdet_lite2/float16/1/efficientdet_lite2.tflite",
         "5d4ebec1029bc9907aeadb9e7b4ac9cb1da6a19d01ad375210a9ae18ba173302"),
    ),
    "gesture": (
        ("gesture_recognizer.task", GOOGLE + "gesture_recognizer/gesture_recognizer/float16/1/gesture_recognizer.task",
         "97952348cf6a6a4915c2ea1496b4b37ebabc50cbbf80571435643c455f2b0482"),
    ),
    "silhouette": (
        ("selfie_segmenter_landscape.tflite", GOOGLE + "image_segmenter/selfie_segmenter_landscape/float16/1/selfie_segmenter_landscape.tflite",
         "490e9ea734313e0de10fa0cd9e3c6133e36ea4db2b7a49bde9ef019f72796b8e"),
    ),
    "caption": (
        ("caption/tokenizer.json", CAPTIONS + "tokenizer.json",
         "6e785cd4f004c9291dadeba7d8d1c2871318d368a1cfcd416c0571dcd8f11413"),
        ("caption/onnx/encoder_model_quantized.onnx", CAPTIONS + "onnx/encoder_model_quantized.onnx",
         "6f6e2e27c11303cf533682184543333e7ecb930a734197a0272a1e408aba2766"),
        ("caption/onnx/decoder_model_merged_quantized.onnx", CAPTIONS + "onnx/decoder_model_merged_quantized.onnx",
         "1f3ec53b5fc3614c0b54ee786755a7ec3007841f57543f8e241499edfadfa98f"),
    ),
}


def download(name, url, expected_hash):
    destination = MODEL_DIR / name
    if destination.is_file():
        with destination.open("rb") as existing:
            if hashlib.file_digest(existing, "sha256").hexdigest() == expected_hash:
                print(f"Verified {name}", flush=True)
                return

    print(f"Downloading {name}", flush=True)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile(dir=destination.parent, delete=False) as output:
        temporary = Path(output.name)
        try:
            digest = hashlib.sha256()
            with urlopen(url, timeout=60) as response:
                while chunk := response.read(1024 * 1024):
                    output.write(chunk)
                    digest.update(chunk)
            if digest.hexdigest() != expected_hash:
                raise RuntimeError(f"Download checksum did not match for {name}. Try again.")
            output.close()
            temporary.replace(destination)
        finally:
            temporary.unlink(missing_ok=True)
    print(f"Downloaded and verified {name}", flush=True)


def main():
    parser = argparse.ArgumentParser(description="Download the pinned local vision models.")
    parser.add_argument("project", nargs="?", default="all", choices=("all", *MODELS))
    args = parser.parse_args()
    projects = MODELS if args.project == "all" else (args.project,)
    for project in projects:
        for name, url, checksum in MODELS[project]:
            download(name, url, checksum)


if __name__ == "__main__":
    raise SystemExit(run_app(main))
