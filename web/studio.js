import { previewBounds, previewX } from "./mirror.mjs";

const apps = {
  "object-motion-lab": ["objects", "Object Motion Lab", "Watch your camera feed with live labels for objects and outlines for moving areas."],
  "gesture-voice-lab": ["gesture", "Gesture Voice Lab", "Hold a hand pose to add a word to a sequence you can speak."],
  "scene-caption-camera": ["caption", "Scene Caption Camera", "Capture a frame, generate a description, and hear the caption aloud."],
  "kinetic-silhouette": ["art", "Kinetic Silhouette", "Step into a particle landscape and watch the parts of your silhouette that move turn gold."],
};
const slug = location.pathname.split("/").filter(Boolean).at(-1) || "object-motion-lab";
const [mode, title, description] = apps[slug] || apps["object-motion-lab"];
const get = (id) => document.getElementById(id);
const studio = get("studio");
const video = get("video");
const canvas = get("overlay");
const overlay = canvas.getContext("2d");
const snapshot = document.createElement("canvas");
const capture = snapshot.getContext("2d", { alpha: false });
const status = get("camera-status");
const toggle = get("camera-toggle");
const mirror = get("mirror-camera");
const mask = get("mask");
const artwork = get("artwork");
const names = get("object-list");
const words = get("words");
const caption = get("caption");
const auto = get("auto-caption");
const mirrorPreference = "webcam-studio-mirror";
const objectColors = ["#5cc4ff", "#ff8ddc", "#ffd55a", "#ffb29c"];
const handPaths = [[0, 1, 2, 3, 4], [0, 5, 6, 7, 8], [5, 9, 10, 11, 12],
  [9, 13, 14, 15, 16], [13, 17, 18, 19, 20], [17, 0]];
let active = null;
let lastCaption = "";
let lastOverlay = null;

try {
  mirror.checked = sessionStorage.getItem(mirrorPreference) !== "false";
} catch {
  // The checkbox still works when browser storage is unavailable.
}

studio.dataset.mode = mode;
document.title = title + " | Webcam Studio";
get("title").textContent = title;
get("description").textContent = description;
get("camera-title").textContent = mode === "art" ? "Particle landscape" : "Camera preview";
for (const link of studio.querySelectorAll("nav a")) {
  if (link.pathname === "/" + slug + "/") link.setAttribute("aria-current", "page");
  else link.removeAttribute("aria-current");
}
for (const panel of studio.querySelectorAll(".panel")) panel.hidden = panel.id !== "panel-" + mode;

function message(text) {
  get("message").textContent = text;
  get("message").hidden = !text;
}

function cameraStatus(state, text) {
  status.dataset.state = state;
  status.textContent = text;
}

function updateCaptionControls() {
  get("describe").disabled = !active?.ready || active.pending;
  get("speak-caption").disabled = !lastCaption;
}

function readWords(sequence) {
  const text = sequence.join(" ") || "No words yet.";
  if (words.textContent !== text) words.textContent = text;
  get("clear-words").disabled = !sequence.length;
  get("speak-words").disabled = !sequence.length;
}

function resetPreview() {
  lastOverlay = null;
  video.hidden = true;
  canvas.hidden = true;
  artwork.hidden = true;
  artwork.removeAttribute("src");
  mask.hidden = true;
  mask.removeAttribute("src");
  get("stage").classList.remove("has-art");
  get("placeholder").hidden = false;
  names.replaceChildren();
  get("object-status").textContent = "Waiting for camera.";
  get("motion-count").querySelector("output").textContent = "—";
  get("gesture-status").textContent = "Waiting for camera.";
  readWords([]);
  get("art-status").textContent = "Waiting for camera.";
  get("body-motion").value = 0;
  get("body-percent").textContent = "0%";
  lastCaption = "";
  caption.textContent = "No caption yet.";
  get("caption-status").textContent = "Start your camera to describe a frame.";
  updateCaptionControls();
}

function stopCamera(error = "") {
  const session = active;
  active = null;
  if (session) {
    clearTimeout(session.timer);
    clearTimeout(session.connectionTimer);
    session.socket?.close();
    session.stream?.getTracks().forEach((track) => track.stop());
  }
  video.srcObject = null;
  window.speechSynthesis?.cancel();
  resetPreview();
  toggle.textContent = "Start camera";
  toggle.dataset.running = "false";
  cameraStatus(error ? "error" : "off", "Camera off");
  message(error);
}

function sendControl(payload) {
  if (active?.ready && active.socket.readyState === WebSocket.OPEN) {
    active.socket.send(JSON.stringify(payload));
  }
}

function sendSettings() {
  const detectionMode = get("detection-mode").value;
  get("show-mask").disabled = detectionMode === "objects";
  if (get("show-mask").disabled || !get("show-mask").checked) mask.hidden = true;
  if (mode === "objects") sendControl({ type: "settings", mode: detectionMode, show_mask: get("show-mask").checked && detectionMode !== "objects" });
  if (mode === "gesture") sendControl({ type: "settings", speak_each: get("speak-each").checked });
  if (mode === "art") sendControl({ type: "settings", view_mask: get("view-mask").checked, mirror: mirror.checked });
}

function updateMirror() {
  studio.dataset.mirrored = String(mirror.checked);
  if (lastOverlay) drawOverlay(lastOverlay);
  if (mode === "art") sendSettings();
}

function speak(text) {
  if (!text) return;
  if (!window.speechSynthesis || !window.SpeechSynthesisUtterance) {
    message("Speech playback is unavailable in this browser.");
    return;
  }
  window.speechSynthesis.cancel();
  window.speechSynthesis.speak(new SpeechSynthesisUtterance(text));
}

function scheduleFrame(session, delay) {
  clearTimeout(session.timer);
  session.timer = setTimeout(() => sendFrame(session), delay);
}

function scheduleNext(session) {
  if (mode !== "caption") scheduleFrame(session, 90);
  else if (auto.checked) scheduleFrame(session, 4000);
}

function sendFrame(session) {
  if (session !== active || !session.ready || session.pending) return;
  clearTimeout(session.timer);
  if (video.readyState < HTMLMediaElement.HAVE_CURRENT_DATA || session.socket.bufferedAmount) {
    scheduleFrame(session, 80);
    return;
  }
  const scale = Math.min(1, 640 / video.videoWidth, 480 / video.videoHeight);
  snapshot.width = Math.max(2, Math.round(video.videoWidth * scale));
  snapshot.height = Math.max(2, Math.round(video.videoHeight * scale));
  capture.drawImage(video, 0, 0, snapshot.width, snapshot.height);
  session.pending = true;
  updateCaptionControls();
  if (mode === "caption") get("caption-status").textContent = "Describing frame…";
  snapshot.toBlob((jpeg) => {
    if (session !== active || session.socket.readyState !== WebSocket.OPEN) return;
    if (jpeg) session.socket.send(jpeg);
    else stopCamera("The browser could not encode a camera frame.");
  }, "image/jpeg", 0.8);
}

function colorFor(label) {
  const sum = Array.from(label).reduce((total, letter) => total + letter.codePointAt(0), 0);
  return objectColors[sum % objectColors.length];
}

function drawBox(box, color, label) {
  const [x, y, width, height] = box;
  const [left, right] = previewBounds(x, width, canvas.width, mirror.checked);
  const top = Math.max(0, y);
  const bottom = Math.min(canvas.height - 1, y + height);
  if (right <= left || bottom <= top) return;
  overlay.strokeStyle = color;
  overlay.lineWidth = 2;
  overlay.strokeRect(left, top, right - left, bottom - top);
  overlay.font = "600 " + Math.max(12, Math.round(canvas.width / 43)) + "px system-ui";
  const widthWithPadding = overlay.measureText(label).width + 10;
  const labelLeft = Math.max(0, Math.min(left, canvas.width - widthWithPadding));
  const labelTop = top >= 23 ? top - 23 : top;
  overlay.fillStyle = color;
  overlay.fillRect(labelLeft, labelTop, widthWithPadding, 23);
  overlay.fillStyle = "#10191c";
  overlay.textBaseline = "middle";
  overlay.fillText(label, labelLeft + 5, labelTop + 12);
}

function drawHands(hands) {
  overlay.strokeStyle = "#f0ca8b";
  overlay.fillStyle = "#f9f0df";
  overlay.lineWidth = 2;
  for (const hand of hands) {
    const points = hand.map(([x, y]) => [previewX(x * canvas.width, canvas.width, mirror.checked), y * canvas.height]);
    for (const path of handPaths) {
      overlay.beginPath();
      overlay.moveTo(...points[path[0]]);
      for (const index of path.slice(1)) overlay.lineTo(...points[index]);
      overlay.stroke();
    }
    for (const [x, y] of points) {
      overlay.beginPath();
      overlay.arc(x, y, 2.5, 0, 2 * Math.PI);
      overlay.fill();
    }
  }
}

function renderObjects(result) {
  for (const box of result.motion) drawBox(box, "#a5eecf", "Motion");
  const rows = result.objects.map((item) => {
    const color = colorFor(item.label);
    const score = Math.round(item.score * 100) + "%";
    drawBox(item.box, color, item.label + " " + score);
    const row = document.createElement("li");
    const label = document.createElement("span");
    const confidence = document.createElement("span");
    label.textContent = item.label;
    confidence.textContent = score;
    row.style.setProperty("--object-color", color);
    row.append(label, confidence);
    return row;
  });
  names.replaceChildren(...rows);
  const selection = get("detection-mode").value;
  get("object-readout").hidden = selection === "motion";
  get("motion-count").hidden = selection === "objects";
  get("object-status").textContent = rows.length ? "" : "No confirmed objects in this frame.";
  get("motion-count").querySelector("output").textContent = String(result.motion.length);
  mask.hidden = !result.mask || !get("show-mask").checked || selection === "objects";
  if (!mask.hidden) mask.src = result.mask;
}

function drawOverlay(result) {
  canvas.width = result.width;
  canvas.height = result.height;
  canvas.hidden = false;
  if (mode === "objects") renderObjects(result);
  if (mode === "gesture") drawHands(result.hands);
}

function renderResult(result) {
  if (mode === "objects" || mode === "gesture") {
    lastOverlay = result;
    drawOverlay(result);
  }
  if (mode === "gesture") {
    get("gesture-status").textContent = result.status;
    readWords(result.words);
    speak(result.spoken);
  }
  if (mode === "caption") {
    lastCaption = result.caption;
    caption.textContent = lastCaption;
    get("caption-status").textContent = "Caption ready.";
    updateCaptionControls();
  }
  if (mode === "art") {
    artwork.src = result.art;
    artwork.hidden = false;
    get("stage").classList.add("has-art");
    get("art-status").textContent = result.body_present ? "Person in view" : "Step into view";
    get("body-motion").value = result.motion_percent;
    get("body-percent").textContent = result.motion_percent.toFixed(1) + "%";
  }
}

function handleMessage(session, data) {
  if (session !== active) return;
  const result = JSON.parse(data);
  if (result.type === "ready") {
    clearTimeout(session.connectionTimer);
    session.ready = true;
    cameraStatus("live", "Camera on");
    sendSettings();
    updateCaptionControls();
    if (mode === "caption") {
      get("caption-status").textContent = "Ready to describe a frame.";
      if (auto.checked) sendFrame(session);
    } else {
      sendFrame(session);
    }
  } else if (result.type === "result") {
    session.pending = false;
    renderResult(result);
    scheduleNext(session);
  } else if (result.type === "gesture") {
    readWords(result.words);
    speak(result.spoken);
  } else if (result.type === "error") {
    session.pending = false;
    if (result.fatal) stopCamera(result.message);
    else {
      message(result.message);
      updateCaptionControls();
      if (mode === "caption") get("caption-status").textContent = "Try describing another frame.";
      scheduleNext(session);
    }
  }
}

async function startCamera() {
  const session = { ready: false, pending: false };
  active = session;
  message("");
  toggle.textContent = "Stop camera";
  toggle.dataset.running = "true";
  cameraStatus("pending", "Opening camera");
  try {
    if (!navigator.mediaDevices?.getUserMedia) {
      throw new Error("Open this app on localhost or HTTPS to use your camera.");
    }
    const stream = await navigator.mediaDevices.getUserMedia({
      audio: false,
      video: { width: { ideal: 640 }, height: { ideal: 480 }, facingMode: "user" },
    });
    if (session !== active) {
      stream.getTracks().forEach((track) => track.stop());
      return;
    }
    session.stream = stream;
    for (const track of stream.getTracks()) track.addEventListener("ended", () => {
      if (active === session) stopCamera("The camera stopped. Start it again to reconnect.");
    });
    video.srcObject = stream;
    await video.play();
    if (session !== active) return;
    video.hidden = false;
    get("placeholder").hidden = true;
    cameraStatus("pending", "Connecting to Python");
    const protocol = location.protocol === "https:" ? "wss:" : "ws:";
    session.socket = new WebSocket(protocol + "//" + location.host + "/ws/" + slug);
    session.socket.addEventListener("message", (event) => handleMessage(session, event.data));
    session.socket.addEventListener("close", () => {
      if (active === session) stopCamera("The Python connection closed. Start the camera to reconnect.");
    });
    session.connectionTimer = setTimeout(() => {
      if (active === session) stopCamera("The Python server took too long to respond.");
    }, 45000);
  } catch (error) {
    if (session !== active) return;
    const text = error.name === "NotAllowedError" ? "Camera permission was denied. Allow it in your browser and try again." : error.message;
    stopCamera(text || "Could not open the camera.");
  }
}

toggle.addEventListener("click", () => active ? stopCamera() : startCamera());
mirror.addEventListener("change", () => {
  updateMirror();
  try {
    sessionStorage.setItem(mirrorPreference, String(mirror.checked));
  } catch {
    // The current page keeps its mirror setting without browser storage.
  }
});
updateMirror();
for (const id of ["detection-mode", "show-mask", "speak-each", "view-mask"]) {
  get(id).addEventListener("change", sendSettings);
}
get("describe").addEventListener("click", () => { if (active) sendFrame(active); });
get("speak-caption").addEventListener("click", () => speak(lastCaption));
get("clear-words").addEventListener("click", () => sendControl({ type: "clear" }));
get("speak-words").addEventListener("click", () => sendControl({ type: "speak" }));
auto.addEventListener("change", () => {
  if (!active) return;
  clearTimeout(active.timer);
  if (auto.checked) sendFrame(active);
});
window.addEventListener("pagehide", () => { if (active) stopCamera(); });
