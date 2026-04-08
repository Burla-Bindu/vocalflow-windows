"""
src/text_injector.py
Injects text at the cursor by:
  1. Saving the current clipboard
  2. Writing the transcript to the clipboard
  3. Simulating Ctrl+V
  4. Restoring the original clipboard
Works in any Windows application.
"""

import time
import sys
import os
import pyperclip
import pyautogui

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.app_state import state


class TextInjector:
    PASTE_DELAY   = 0.05   # seconds between clipboard write and Ctrl+V
    RESTORE_DELAY = 0.30   # seconds after paste before clipboard restore

    def inject(self, text: str) -> bool:
        if not text or not text.strip():
            state.set_status("⚠️ Nothing to inject")
            return False

        prev = ""
        try:
            prev = pyperclip.paste()
        except Exception:
            pass

        try:
            pyperclip.copy(text)
            time.sleep(self.PASTE_DELAY)
            pyautogui.hotkey("ctrl", "v")
            time.sleep(self.RESTORE_DELAY)
            # restore
            if prev:
                pyperclip.copy(prev)
            state.set_status(f"✅ Injected: {text[:40]}{'…' if len(text)>40 else ''}")
            print(f"[Injector] injected: {text!r}")
            return True
        except Exception as e:
            state.set_status(f"❌ Inject error: {e}")
            print(f"[Injector] error: {e}")
            try:
                if prev:
                    pyperclip.copy(prev)
            except Exception:
                pass
            return False
