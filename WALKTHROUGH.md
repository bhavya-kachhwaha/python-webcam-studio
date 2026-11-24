# Python Webcam Studio, line by line

Start with the function map to see what calls what. Open each line-by-line chapter beside its source file. Every numbered explanation matches a nonblank line. The browser interface and desktop previews share the Python processing chapters.

| Chapter | What you’ll follow |
| --- | --- |
| [How every function connects](WALKTHROUGH-FUNCTIONS.md) | Follow one frame from camera to interface and look up each function’s role and callers. |
| [Browser interface](WALKTHROUGH-WEB.md) | Request webcam access, sample JPEGs, send one frame at a time, and display or speak the returned result. |
| [Python web server](WALKTHROUGH-SERVER.md) | Follow a WebSocket connection through validation, session state, model inference, and response encoding. |
| [Object Motion Lab](WALKTHROUGH-OBJECTS.md) | Compare grayscale frames, find contours, recognize COCO objects, stabilize boxes, and check both pipelines in tests. |
| [Gesture Voice Lab](WALKTHROUGH-GESTURE.md) | Turn recognized hand poses into timed word selections and read the sequence aloud. |
| [Scene Caption Camera](WALKTHROUGH-CAPTIONS.md) | Convert an image into model input, generate a caption token by token, and display it while the camera keeps running. |
| [Kinetic Silhouette](WALKTHROUGH-SILHOUETTE.md) | Segment a person, measure pixel changes inside them, and render the movement as gold particles. |
| [Shared camera and speech](WALKTHROUGH-SHARED.md) | Open the webcam or a recording, handle display and keys, and call the operating system’s speech engine. |
| [Dependencies and model setup](WALKTHROUGH-SETUP.md) | Install the packages, download the pinned assets, and verify their checksums. |
| [Node.js launch and Linux packaging](WALKTHROUGH-LAUNCH.md) | Start the shared Python server from npm, build the container, and follow the GitHub checks. |

## Start with two frames

Run `.venv/bin/python web_server.py`, then open [Object Motion Lab](http://127.0.0.1:8894/object-motion-lab/). Choose **Motion only**, enable **Show motion mask**, and start the camera. The Terminal command opens the same lesson in native windows and lets you change the threshold and minimum area.

```bash
.venv/bin/python motion_detector.py --mode motion --show-mask
```

1. Hold the camera still and wave a hand. Watch the binary mask turn white where brightness changes and the color preview draw green rectangles around large regions.
2. Keep your hand still. The next frames match more closely, so the mask darkens and the rectangles clear.
3. Try the same movement with `--threshold 10` and then `--threshold 45`. The threshold acts on each pixel. Next fix the threshold and compare `--min-area 50` with `--min-area 800`. The area filter acts on whole contours, so small white patches can stay in the mask after their boxes disappear.
4. Open `.venv/bin/python motion_detector.py --show-mask` and hold a cup still. The named object label and the motion mask now provide two measurements of the same frame.

A recorded video gives you repeatable input for all four apps. Pass `--video FILE` and change one setting at a time. After editing the code, run `.venv/bin/python -m unittest -v`.

[OpenCV video capture](https://docs.opencv.org/4.x/dd/d43/tutorial_py_video_display.html) · [OpenCV morphology](https://docs.opencv.org/4.x/d9/d61/tutorial_py_morphological_ops.html) · [OpenCV contours](https://docs.opencv.org/4.x/d4/d73/tutorial_py_contours_begin.html) · [MediaPipe Object Detector](https://ai.google.dev/edge/mediapipe/solutions/vision/object_detector/python)
