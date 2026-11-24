import shutil
import subprocess


class Speech:
    def __init__(self):
        self.engine = shutil.which("say") or shutil.which("espeak-ng") or shutil.which("espeak")
        self.playback = None

    def __enter__(self):
        return self

    def speak(self, text):
        if not text.strip():
            return
        if self.engine is None:
            raise RuntimeError("Speech needs macOS say or an installed espeak-ng command.")
        self.stop()
        self.playback = subprocess.Popen([self.engine, "--", text], stdin=subprocess.DEVNULL)

    def stop(self):
        if self.playback is not None and self.playback.poll() is None:
            self.playback.terminate()
            try:
                self.playback.wait(timeout=1)
            except subprocess.TimeoutExpired:
                self.playback.kill()
                self.playback.wait()

    def __exit__(self, error_type, error, traceback):
        self.stop()
