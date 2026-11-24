# Python Webcam Studio

Four webcam apps share one Python and OpenCV implementation. The web interface and Terminal commands call the same object, motion, gesture, caption, and silhouette processing code.

## Open in your browser

From this folder, start the Python server.

```bash
.venv/bin/python web_server.py
```

You can also start the same Python server with Node.js 22 or newer. Add an app slug to print a link that opens that mode.

```bash
npm start -- object-motion-lab
```

Open [Webcam Studio](http://127.0.0.1:8894/) in Chrome or another browser with camera access. Choose an app and click **Start camera**. The camera preview plays directly in the browser. It sends one sampled frame at a time to Python and draws the returned boxes or hand landmarks over the preview. For Scene Caption Camera, frames are sent when you press **Describe frame** or enable automatic captions. Kinetic Silhouette displays the artwork rendered by Python. Speech plays through the browser on your device.

**Mirror preview** is on by default. Toggle it to switch the orientation of your preview, outlines, landmarks, and silhouette. The local server processes sampled images in memory. **Stop camera** releases the webcam and closes the connection. Each tab gets its own motion history and word sequence. On a hosted release, sampled frames reach the Python server over HTTPS and secure WebSockets.

## Run from Terminal

Run these commands from this folder. The Mac's Python environment and model files are already installed here.

| App | Command | Controls |
| --- | --- | --- |
| Object Motion Lab | `.venv/bin/python motion_detector.py --show-mask` | Color labels show named objects and confidence. Green outlines mark frame-to-frame motion. The optional mask window shows the changed pixels. |
| Gesture Voice Lab | `.venv/bin/python gesture_voice.py` | Hold a supported pose for 1.5 seconds, then lower your hands briefly. **S** speaks the sequence, **C** clears it, and holding both open palms for two seconds also speaks it. |
| Scene Caption Camera | `.venv/bin/python scene_caption.py` | **C** describes the current frame, **S** speaks the latest caption, and **A** toggles periodic captions. Use `--auto` to start with periodic captions on. |
| Kinetic Silhouette | `.venv/bin/python kinetic_silhouette.py` | Stand in view and move. Your outline appears in blue and violet, and moving areas turn gold. **M** switches between the art and the mask. |

Click the preview and press **Q** or **Esc** to quit. Run one webcam app at a time. If macOS asks for camera access, allow it for the launcher. You can also check **System Settings → Privacy & Security → Camera** and try `--camera 1` for a second camera. [Apple's camera access guide](https://support.apple.com/guide/mac-help/control-access-to-your-camera-mchlf6d108da/mac)

### Object and motion modes

```bash
.venv/bin/python motion_detector.py --mode objects --confidence 0.5
.venv/bin/python motion_detector.py --mode motion --threshold 14 --min-area 120 --show-mask
.venv/bin/python motion_detector.py --video clip.mp4 --show-mask
```

`--mode both` is the default. The AI model recognizes 80 COCO categories, including person, cup, chair, cat, and dog. Two matching model samples confirm a box. Motion mode uses OpenCV frame differencing and works without model files. Lower `--threshold` for subtler brightness changes or lower `--min-area` for smaller movement regions. Lighting changes and camera shake can trigger motion boxes.

### Supported gestures

Gesture Voice Lab maps seven static poses to a small vocabulary. It uses the Mac's built-in `say` command, and systems with `espeak-ng` or `espeak` can use those engines. Add `--speak-each` to hear each entry as you make it.

| Pose | Word or phrase |
| --- | --- |
| Two fingers in a V | Use |
| Open palm | Technology |
| Index finger pointing up | For |
| Thumbs up | Help |
| Thumbs down | Not |
| Closed fist | War |
| Thumb, index, and little finger extended | I love you |

Scene Caption Camera runs a quantized ViT–GPT-2 model in Python. The first caption loads the model in the background, and the live preview stays open while it works. Treat the caption as the model's best guess about the frame. In Kinetic Silhouette, AI identifies person pixels and classical frame differencing measures movement inside that area. [MediaPipe's privacy notice](https://pypi.org/project/mediapipe/#privacy-notice)

## Set up another machine

Use Python 3.12. These commands use `uv`, and the model download is about 269 MB.

```bash
uv venv --python 3.12
uv pip install --python .venv/bin/python -r requirements.txt
.venv/bin/python download_models.py
```

If upgrading this folder's earlier motion-only environment, first run `uv pip uninstall --python .venv/bin/python opencv-python`. The suite uses `opencv-contrib-python` for MediaPipe compatibility. Both wheels provide `cv2`, so use one per environment.

With CPython 3.12 and pip, you can use `python3.12 -m venv .venv` and `.venv/bin/python -m pip install -r requirements.txt` for the first two steps. To download only one project's model, pass `objects`, `gesture`, `caption`, or `silhouette` to `download_models.py`.

## Learn and test

Start with the [line-by-line walkthrough](WALKTHROUGH.md). Follow a frame from the browser through the WebSocket and into the same Python processing code used in the Terminal version. The guide also covers each app, setup, and tests.

```bash
.venv/bin/python -m unittest -v
npm test
```

The unit tests use generated inputs and can run with the webcam closed. The recorded-video path is useful for repeating motion and recognition experiments under the same conditions.

## Run the Linux container

```bash
docker build -t python-webcam-studio .
docker run --rm -p 127.0.0.1:7860:7860 python-webcam-studio
```

Open [the container preview](http://127.0.0.1:7860/). The image downloads and verifies the model weights at build time. A public deployment needs a native Python container host and a same-origin HTTPS route that forwards WebSocket upgrades.

The project was inspired by [Sign Language to Voice System](https://github.com/tubakhxn/sign-language-to-voice-system), [See and Tell](https://github.com/tubakhxn/see-and-tell), and [Living Particle Artwork](https://github.com/tubakhxn/Living-Particle-Artwork).
