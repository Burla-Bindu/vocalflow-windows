"""
src/hotkey_manager.py
Monitors a global hold-to-record hotkey using the `keyboard` library.
Press → on_press callback fires.
Release → on_release callback fires.
"""

import threading
import sys
import os
import keyboard

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.app_state import state


class HotkeyManager:
    def __init__(self, on_press=None, on_release=None):
        self._on_press   = on_press
        self._on_release = on_release
        self._holding    = False
        self._key        = None
        self._lock       = threading.Lock()

    # ── Public ────────────────────────────────────────────────────────

    def start(self):
        self._register(state.hotkey)
        print(f"[Hotkey] Listening — hold '{state.hotkey}' to record.")

    def stop(self):
        self._unregister()
        print("[Hotkey] Stopped.")

    def change_key(self, new_key: str):
        self._unregister()
        state.hotkey = new_key
        self._register(new_key)
        print(f"[Hotkey] Changed to '{new_key}'.")

    # ── Internal ──────────────────────────────────────────────────────

    def _register(self, key: str):
        self._key = key

        def _press(e):
            with self._lock:
                if self._holding:
                    return
                self._holding = True
            print(f"[Hotkey] pressed: {key}")
            if self._on_press:
                threading.Thread(target=self._on_press, daemon=True).start()

        def _release(e):
            with self._lock:
                if not self._holding:
                    return
                self._holding = False
            print(f"[Hotkey] released: {key}")
            if self._on_release:
                threading.Thread(target=self._on_release, daemon=True).start()

        try:
            keyboard.on_press_key(key,   _press,   suppress=False)
            keyboard.on_release_key(key, _release, suppress=False)
        except Exception as e:
            print(f"[Hotkey] Register error: {e}")
            state.set_status(f"❌ Hotkey error — try running as Admin")

    def _unregister(self):
        if self._key:
            try:
                keyboard.unhook_key(self._key)
            except Exception:
                pass
        self._holding = False
        self._key = None
