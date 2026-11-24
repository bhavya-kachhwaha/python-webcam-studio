import { spawn } from "node:child_process";
import { existsSync } from "node:fs";
import { fileURLToPath } from "node:url";

const studio = new URL("../", import.meta.url);
const apps = ["object-motion-lab", "gesture-voice-lab", "scene-caption-camera", "kinetic-silhouette"];
const [mode = "", ...extra] = process.argv.slice(2);
const venv = process.platform === "win32" ? ".venv/Scripts/python.exe" : ".venv/bin/python";
const python = process.env.STUDIO_PYTHON || fileURLToPath(new URL(venv, studio));

if (extra.length || (mode && !apps.includes(mode))) {
  console.error("Choose one app: " + apps.join(", "));
  process.exitCode = 2;
} else if (!process.env.STUDIO_PYTHON && !existsSync(python)) {
  console.error("Set up the Python environment and models using README.md, then retry npm start.");
  process.exitCode = 1;
} else {
  console.log("Webcam Studio  http://127.0.0.1:8894/" + (mode ? mode + "/" : ""));
  const child = spawn(python, ["web_server.py"], { cwd: fileURLToPath(studio), stdio: "inherit" });
  for (const signal of ["SIGINT", "SIGTERM"]) process.once(signal, () => child.kill(signal));
  child.on("error", (error) => {
    console.error(error.message);
    process.exitCode = 1;
  });
  child.on("exit", (code, signal) => {
    process.exitCode = code ?? (signal === "SIGINT" || signal === "SIGTERM" ? 0 : 1);
  });
}
