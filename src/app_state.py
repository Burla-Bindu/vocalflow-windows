"""
src/app_state.py
Shared singleton that every module imports.
Holds runtime state + persists user preferences to JSON.
"""

import json
import os
import sys
import threading

# Allow imports from project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config


class AppState:
    def __init__(self):
        self._lock = threading.Lock()

        # ── Keys (from config.py — never saved to disk) ───────────────
        self.deepgram_api_key: str = config.DEEPGRAM_API_KEY
        self.groq_api_key:     str = config.GROQ_API_KEY

        # ── Deepgram ──────────────────────────────────────────────────
        self.deepgram_model:    str = config.DEEPGRAM_MODEL
        self.deepgram_language: str = config.DEEPGRAM_LANGUAGE

        # ── Groq ──────────────────────────────────────────────────────
        self.groq_model:              str  = config.GROQ_MODEL
        self.groq_enabled:            bool = config.GROQ_ENABLED
        self.groq_mode:               str  = config.GROQ_MODE
        self.groq_translation_target: str  = config.GROQ_TRANSLATION_TARGET

        # ── Hotkey ────────────────────────────────────────────────────
        self.hotkey: str = config.DEFAULT_HOTKEY

        # ── Runtime ───────────────────────────────────────────────────
        self.is_recording:   bool = False
        self.is_processing:  bool = False
        self.last_transcript: str = ""
        self.status_message:  str = "Ready"

        # ── UI callbacks (set by main.py) ─────────────────────────────
        self.on_status_change:    callable = None   # fn(msg: str)
        self.on_recording_change: callable = None   # fn(recording: bool)

        self._load()

    # ── Persistence ───────────────────────────────────────────────────

    _PERSIST_KEYS = [
        "hotkey", "deepgram_model", "deepgram_language",
        "groq_model", "groq_enabled", "groq_mode", "groq_translation_target",
    ]

    def _load(self):
        path = config.SETTINGS_FILE
        if not os.path.exists(path):
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            for k in self._PERSIST_KEYS:
                if k in data:
                    setattr(self, k, data[k])
        except Exception as e:
            print(f"[AppState] load error: {e}")

    def save(self):
        data = {k: getattr(self, k) for k in self._PERSIST_KEYS}
        try:
            with open(config.SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"[AppState] save error: {e}")

    # ── Helpers ───────────────────────────────────────────────────────

    def set_status(self, msg: str):
        with self._lock:
            self.status_message = msg
        if self.on_status_change:
            try:
                self.on_status_change(msg)
            except Exception:
                pass

    def set_recording(self, value: bool):
        with self._lock:
            self.is_recording = value
        if self.on_recording_change:
            try:
                self.on_recording_change(value)
            except Exception:
                pass


# ── Singleton ─────────────────────────────────────────────────────────
state = AppState()
