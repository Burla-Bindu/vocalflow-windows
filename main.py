"""
main.py — VocalFlow Windows  entry point
========================================
Starts the system-tray app and wires together:
    hotkey → audio → Deepgram → (Groq) → text injection

Run:
    python main.py          (needs admin for global hotkey)
    or double-click run.bat
"""

import sys
import threading
import tkinter as tk

from src.app_state      import state
from src.audio_engine   import AudioEngine
from src.deepgram_service import DeepgramService
from src.groq_service   import GroqService
from src.text_injector  import TextInjector
from src.hotkey_manager import HotkeyManager
from src.tray_controller import TrayController
import config


class VocalFlowApp:
    def __init__(self):
        # Hidden Tk root (all Tkinter windows must share one root)
        self._root = tk.Tk()
        self._root.withdraw()
        self._root.title(config.APP_NAME)

        # Services
        self._audio    = AudioEngine()
        self._deepgram = DeepgramService()
        self._groq     = GroqService()
        self._injector = TextInjector()

        # Controllers
        self._hotkey = HotkeyManager(
            on_press   = self._on_press,
            on_release = self._on_release,
        )
        self._tray = TrayController(
            root     = self._root,
            on_quit  = self._shutdown,
        )

        # Wire state → UI
        state.on_status_change    = self._tray.set_status
        state.on_recording_change = self._tray.set_recording

    # ── Lifecycle ─────────────────────────────────────────────────────

    def run(self):
        print(f"[VocalFlow] {config.APP_NAME} v{config.APP_VERSION} starting…")
        self._tray.start(on_hotkey_change=self._hotkey.change_key)
        self._hotkey.start()
        state.set_status("Ready — hold hotkey to dictate")
        print(f"[VocalFlow] Hold '{state.hotkey}' to record. "
              "Right-click tray icon for menu.")
        try:
            self._root.mainloop()
        except KeyboardInterrupt:
            self._shutdown()

    def _shutdown(self):
        print("[VocalFlow] Shutting down…")
        self._hotkey.stop()
        state.save()
        try:
            self._root.quit()
        except Exception:
            pass
        sys.exit(0)

    # ── Hotkey callbacks (run on background threads) ──────────────────

    def _on_press(self):
        """Hotkey held down → start mic."""
        if state.is_recording or state.is_processing:
            return
        state.set_recording(True)
        self._audio.start_recording()

    def _on_release(self):
        """Hotkey released → transcribe → (post-process) → inject."""
        if not state.is_recording:
            return
        state.set_recording(False)
        state.is_processing = True

        # 1. Capture audio
        pcm = self._audio.stop_recording()
        if not pcm:
            state.set_status("⚠️ No audio captured — hold longer")
            state.is_processing = False
            return

        # 2. Transcribe
        text = self._deepgram.transcribe(pcm)
        if not text:
            state.set_status("⚠️ Nothing recognised")
            state.is_processing = False
            return

        # 3. Optional Groq post-processing
        if state.groq_enabled:
            state.set_status("⚡ Post-processing…")
            text = self._groq.process(text)

        # 4. Inject at cursor
        state.last_transcript = text
        self._injector.inject(text)
        state.is_processing = False


# ── Entry point ───────────────────────────────────────────────────────

if __name__ == "__main__":
    app = VocalFlowApp()
    app.run()
