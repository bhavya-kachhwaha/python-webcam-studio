import asyncio
import base64
import json
import logging
from contextlib import asynccontextmanager, suppress
from io import BytesIO
from pathlib import Path
from time import monotonic

import cv2
import numpy as np
import uvicorn
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image
from starlette.concurrency import run_in_threadpool

from gesture_voice import GestureSession
from kinetic_silhouette import SilhouetteSession
from motion_detector import ObjectMotionSession
from scene_caption import Captioner


WEB = Path(__file__).resolve().parent / "web"
OBJECTS = "object-motion-lab"
GESTURES = "gesture-voice-lab"
CAPTIONS = "scene-caption-camera"
SILHOUETTE = "kinetic-silhouette"
PROCESSORS = {OBJECTS: ObjectMotionSession, GESTURES: GestureSession, SILHOUETTE: SilhouetteSession}
MODES = {*PROCESSORS, CAPTIONS}
MAX_MESSAGE = 512 * 1024
LOG = logging.getLogger("uvicorn.error")


@asynccontextmanager
async def lifespan(app):
    app.state.captioner = Captioner()
    app.state.caption_lock = asyncio.Lock()
    app.state.slots = asyncio.Semaphore(4)
    yield


app = FastAPI(lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None)
app.mount("/static", StaticFiles(directory=WEB), name="static")


@app.get("/")
@app.get("/{mode}/")
async def page(mode=OBJECTS):
    if mode not in MODES:
        raise HTTPException(status_code=404)
    return FileResponse(WEB / "index.html")


def decode_frame(payload):
    if not payload or len(payload) > MAX_MESSAGE:
        raise ValueError("Send one JPEG frame up to 512 KB.")
    try:
        with Image.open(BytesIO(payload), formats=["JPEG"]) as image:
            if not (2 <= image.width <= 640 and 2 <= image.height <= 480):
                raise ValueError("Frame dimensions must fit within 640 by 480 pixels.")
            rgb = np.asarray(image.convert("RGB"))
    except (OSError, Image.DecompressionBombError) as error:
        raise ValueError("The frame must be a readable JPEG image.") from error
    return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)


def image_url(image, extension, mime):
    ok, encoded = cv2.imencode(extension, image)
    if not ok:
        raise RuntimeError("Could not encode the processed image.")
    return f"data:image/{mime};base64,{base64.b64encode(encoded).decode('ascii')}"


def infer(session, frame, now):
    result = session.process(frame, now)
    if result.get("mask") is not None:
        result["mask"] = image_url(result["mask"], ".png", "png")
    if result.get("art") is not None:
        art = cv2.resize(result["art"], (720, 405), interpolation=cv2.INTER_AREA)
        result["art"] = image_url(art, ".jpg", "jpeg")
    return result


def apply_command(mode, session, message):
    command = json.loads(message)
    if not isinstance(command, dict):
        raise ValueError("The control message must be an object.")
    action = command.get("type")
    if action == "settings":
        if mode == OBJECTS:
            view = command.get("mode", session.mode)
            if view not in ("both", "objects", "motion"):
                raise ValueError("Choose objects, motion, or both.")
            session.mode = view
            session.show_mask = command.get("show_mask", session.show_mask) is True
        if mode == GESTURES:
            session.speak_each = command.get("speak_each", session.speak_each) is True
        if mode == SILHOUETTE:
            session.view_mask = command.get("view_mask", session.view_mask) is True
            session.mirror = command.get("mirror", session.mirror) is True
        return None
    if mode == GESTURES and action in ("clear", "speak"):
        if action == "clear":
            session.clear()
        return {"type": "gesture", "words": session.words.copy(),
                "spoken": session.utterance() if action == "speak" else None}
    raise ValueError("Unknown control message.")


def open_session(mode):
    factory = PROCESSORS.get(mode)
    return factory().__enter__() if factory else None


async def frame_response(state, mode, session, payload):
    frame = await run_in_threadpool(decode_frame, payload)
    if mode == CAPTIONS:
        async with state.caption_lock:
            caption = await run_in_threadpool(state.captioner.describe, frame)
        result = {"caption": caption}
    else:
        result = await run_in_threadpool(infer, session, frame, monotonic())
    height, width = frame.shape[:2]
    return {"type": "result", "width": width, "height": height, **result}


@app.websocket("/ws/{mode}")
async def stream(websocket: WebSocket, mode: str):
    host = websocket.headers.get("host")
    origin = websocket.headers.get("origin")
    if mode not in MODES or origin not in (f"http://{host}", f"https://{host}"):
        await websocket.close(code=1008)
        return

    await websocket.accept()
    state = websocket.app.state
    slots = state.slots
    if slots.locked():
        await websocket.send_json({"type": "error", "message": "Studio is busy. Try again shortly.", "fatal": True})
        await websocket.close(code=1013)
        return

    async with slots:
        session = None
        try:
            session = await run_in_threadpool(open_session, mode)
            await websocket.send_json({"type": "ready"})
            while True:
                packet = await asyncio.wait_for(websocket.receive(), timeout=180)
                if packet["type"] == "websocket.disconnect":
                    return
                try:
                    if packet.get("bytes") is not None:
                        response = await frame_response(state, mode, session, packet.pop("bytes"))
                    else:
                        response = apply_command(mode, session, packet["text"])
                    if response is not None:
                        await websocket.send_json(response)
                except ValueError as error:
                    message = "Invalid control message." if isinstance(error, json.JSONDecodeError) else str(error)
                    await websocket.send_json({"type": "error", "message": message, "fatal": False})
        except WebSocketDisconnect:
            pass
        except TimeoutError:
            with suppress(WebSocketDisconnect, RuntimeError):
                await websocket.send_json({"type": "error", "message": "Session paused. Start the camera again.", "fatal": True})
        except Exception:
            LOG.exception("Python vision session failed for %s", mode)
            with suppress(WebSocketDisconnect, RuntimeError):
                await websocket.send_json({"type": "error", "message": "Python processing failed. Check the server and model setup.", "fatal": True})
        finally:
            try:
                if session is not None:
                    await run_in_threadpool(session.__exit__, None, None, None)
            finally:
                with suppress(WebSocketDisconnect, RuntimeError):
                    await websocket.close()


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8894, ws="websockets", ws_max_size=MAX_MESSAGE, ws_max_queue=1)
