"""
src/tray_controller.py
Windows system-tray icon (via pystray + Pillow).
Menu: API Balances | Settings | About | Quit
Icon turns red while recording, blue when idle.
"""

import threading
import tkinter as tk
from tkinter import messagebox
import sys
import os
import pystray
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config
from src.settings_window import SettingsWindow
from src.balance_window import BalanceWindow


def _make_icon(recording: bool) -> Image.Image:
    """Draw a 64×64 microphone icon. Red when recording, blue otherwise."""
    sz  = 64
    img = Image.new("RGBA", (sz, sz), (0, 0, 0, 0))
    d   = ImageDraw.Draw(img)
    col = "#e64553" if recording else "#89b4fa"

    # mic body
    d.rounded_rectangle([20, 8, 44, 40], radius=8, fill=col)
    # stand arc
    d.arc([12, 28, 52, 54], start=0, end=180, fill=col, width=4)
    # stem
    d.line([32, 54, 32, 62], fill=col, width=4)
    # base bar
    d.line([22, 62, 42, 62], fill=col, width=4)
    return img


class TrayController:
    def __init__(self, root: tk.Tk, on_quit=None):
        self._root    = root
        self._on_quit = on_quit
        self._tray: pystray.Icon = None
        self._settings_win = None
        self._balance_win  = None
        self._hk_change_cb = None

    def start(self, on_hotkey_change=None):
        self._hk_change_cb = on_hotkey_change
        self._tray = pystray.Icon(
            config.APP_NAME,
            _make_icon(False),
            f"{config.APP_NAME}  —  Ready",
            menu=pystray.Menu(
                pystray.MenuItem(
                    f"{config.APP_NAME} v{config.APP_VERSION}", None, enabled=False),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("📊  API Balances", self._open_balance),
                pystray.MenuItem("⚙️  Settings",     self._open_settings),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("❓  About",  self._about),
                pystray.MenuItem("🚪  Quit",   self._quit),
            ),
        )
        threading.Thread(target=self._tray.run, daemon=True).start()
        print("[Tray] System-tray icon started.")

    def stop(self):
        if self._tray:
            try:
                self._tray.stop()
            except Exception:
                pass

    # ── Called by main.py via state callbacks ─────────────────────────

    def set_status(self, msg: str):
        if self._tray:
            self._tray.title = f"{config.APP_NAME}  —  {msg}"

    def set_recording(self, recording: bool):
        if self._tray:
            self._tray.icon  = _make_icon(recording)
            self._tray.title = (
                f"{config.APP_NAME}  —  🔴 Recording…"
                if recording else
                f"{config.APP_NAME}  —  Ready"
            )

    # ── Menu actions ─────────────────────────────────────────────────

    def _open_balance(self, *_):
        self._root.after(0, self._open_balance_ui)

    def _open_balance_ui(self):
        if not self._balance_win:
            self._balance_win = BalanceWindow()
        self._balance_win.show()

    def _open_settings(self, *_):
        self._root.after(0, self._open_settings_ui)

    def _open_settings_ui(self):
        win = SettingsWindow(on_hotkey_change=self._hk_change_cb)
        win.show()

    def _about(self, *_):
        self._root.after(0, lambda: messagebox.showinfo(
            f"About {config.APP_NAME}",
            f"{config.APP_NAME}  v{config.APP_VERSION}\n\n"
            "Windows port of VocalFlow (macOS).\n\n"
            "Hold your configured hotkey to record.\n"
            "Release — speech is transcribed and pasted\n"
            "at your cursor in any application.\n\n"
            "Powered by Deepgram + Groq.",
        ))

    def _quit(self, *_):
        self.stop()
        if self._on_quit:
            self._on_quit()
        self._root.after(0, self._root.destroy)
