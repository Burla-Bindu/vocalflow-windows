"""
src/settings_window.py
Full Tkinter settings panel:
  • Deepgram key / model / language
  • Groq key / model / post-processing mode
  • Hotkey selection
"""

import threading
import tkinter as tk
from tkinter import ttk, messagebox, font as tkf
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.app_state import state
from src.deepgram_service import DeepgramService
from src.groq_service import GroqService

BG    = "#1e1e2e"
CARD  = "#2a2a3e"
FG    = "#cdd6f4"
MUTED = "#6c7086"
BLUE  = "#89b4fa"
PURP  = "#cba6f7"
ENTRY = "#313244"

HOTKEYS   = ["right alt", "right ctrl", "caps lock", "right shift", "f9", "f10", "f12"]
GROQ_MODES = ["spelling", "grammar", "translation", "codemix"]


class SettingsWindow:
    def __init__(self, on_hotkey_change=None):
        self._on_hotkey_change = on_hotkey_change
        self._dg   = DeepgramService()
        self._groq = GroqService()
        self._win  = None

    def show(self):
        if self._win and self._win.winfo_exists():
            self._win.lift()
            self._win.focus_force()
            return
        self._build()

    # ── Build ─────────────────────────────────────────────────────────

    def _build(self):
        self._win = tk.Toplevel()
        self._win.title("Settings — VocalFlow")
        self._win.geometry("520x640")
        self._win.resizable(False, False)
        self._win.configure(bg=BG)
        self._win.grab_set()

        F_TITLE = tkf.Font(family="Segoe UI", size=14, weight="bold")
        F_SEC   = tkf.Font(family="Segoe UI", size=10, weight="bold")
        F_BODY  = tkf.Font(family="Segoe UI", size=10)
        F_SMALL = tkf.Font(family="Segoe UI", size=9)
        F_BTN   = tkf.Font(family="Segoe UI", size=10, weight="bold")
        F_MONO  = tkf.Font(family="Consolas",  size=9)

        tk.Label(self._win, text="⚙️  Settings",
                 font=F_TITLE, bg=BG, fg=FG).pack(pady=(20, 2))
        tk.Label(self._win, text="Configure VocalFlow for Windows",
                 font=F_SMALL, bg=BG, fg=MUTED).pack(pady=(0, 12))

        wrap = tk.Frame(self._win, bg=BG)
        wrap.pack(fill="both", padx=24)

        # ── Deepgram ──────────────────────────────────────────────────
        self._sec(wrap, "🎙️  Deepgram", F_SEC)

        self._dg_key = tk.StringVar(value=state.deepgram_api_key)
        self._entry_row(wrap, "API Key", self._dg_key, F_BODY, F_MONO, hide=True)

        # model row with Fetch button
        dg_m = self._row_frame(wrap)
        tk.Label(dg_m, text="Model", width=16, anchor="w",
                 font=F_BODY, bg=CARD, fg=FG).pack(side="left", padx=12, pady=8)
        self._dg_model = tk.StringVar(value=state.deepgram_model)
        self._dg_model_cb = ttk.Combobox(dg_m, textvariable=self._dg_model,
                                          state="readonly", width=20)
        self._dg_model_cb["values"] = [state.deepgram_model]
        self._dg_model_cb.pack(side="left", padx=4)
        tk.Button(dg_m, text="Fetch", command=self._fetch_dg,
                  bg=BLUE, fg=BG, font=F_SMALL, relief="flat",
                  padx=8, pady=3, cursor="hand2").pack(side="left", padx=6)

        # language
        dg_l = self._row_frame(wrap)
        tk.Label(dg_l, text="Language", width=16, anchor="w",
                 font=F_BODY, bg=CARD, fg=FG).pack(side="left", padx=12, pady=8)
        self._lang = tk.StringVar(value=state.deepgram_language)
        tk.Entry(dg_l, textvariable=self._lang, width=16,
                 bg=ENTRY, fg=FG, insertbackground=FG,
                 relief="flat", font=F_BODY).pack(side="left", padx=4)

        # ── Groq ──────────────────────────────────────────────────────
        self._sec(wrap, "⚡  Groq  (optional)", F_SEC)

        self._groq_key = tk.StringVar(value=state.groq_api_key)
        self._entry_row(wrap, "API Key", self._groq_key, F_BODY, F_MONO, hide=True)

        gq_m = self._row_frame(wrap)
        tk.Label(gq_m, text="Model", width=16, anchor="w",
                 font=F_BODY, bg=CARD, fg=FG).pack(side="left", padx=12, pady=8)
        self._groq_model = tk.StringVar(value=state.groq_model)
        self._groq_model_cb = ttk.Combobox(gq_m, textvariable=self._groq_model,
                                             state="readonly", width=20)
        self._groq_model_cb["values"] = [state.groq_model]
        self._groq_model_cb.pack(side="left", padx=4)
        tk.Button(gq_m, text="Fetch", command=self._fetch_groq,
                  bg=PURP, fg=BG, font=F_SMALL, relief="flat",
                  padx=8, pady=3, cursor="hand2").pack(side="left", padx=6)

        # enable checkbox
        en = self._row_frame(wrap)
        tk.Label(en, text="Post-processing", width=16, anchor="w",
                 font=F_BODY, bg=CARD, fg=FG).pack(side="left", padx=12, pady=8)
        self._groq_en = tk.BooleanVar(value=state.groq_enabled)
        tk.Checkbutton(en, text="Enabled", variable=self._groq_en,
                       bg=CARD, fg=FG, selectcolor=ENTRY,
                       activebackground=CARD, font=F_BODY).pack(side="left")

        # mode
        md = self._row_frame(wrap)
        tk.Label(md, text="Mode", width=16, anchor="w",
                 font=F_BODY, bg=CARD, fg=FG).pack(side="left", padx=12, pady=8)
        self._groq_mode = tk.StringVar(value=state.groq_mode)
        ttk.Combobox(md, textvariable=self._groq_mode,
                     values=GROQ_MODES, state="readonly", width=16).pack(side="left", padx=4)

        # translation target
        tr = self._row_frame(wrap)
        tk.Label(tr, text="Translate to", width=16, anchor="w",
                 font=F_BODY, bg=CARD, fg=FG).pack(side="left", padx=12, pady=8)
        self._trans = tk.StringVar(value=state.groq_translation_target)
        tk.Entry(tr, textvariable=self._trans, width=14,
                 bg=ENTRY, fg=FG, insertbackground=FG,
                 relief="flat", font=F_BODY).pack(side="left", padx=4)

        # ── Hotkey ────────────────────────────────────────────────────
        self._sec(wrap, "⌨️  Hold-to-Record Hotkey", F_SEC)

        hk = self._row_frame(wrap)
        tk.Label(hk, text="Hotkey", width=16, anchor="w",
                 font=F_BODY, bg=CARD, fg=FG).pack(side="left", padx=12, pady=8)
        self._hotkey = tk.StringVar(value=state.hotkey)
        ttk.Combobox(hk, textvariable=self._hotkey,
                     values=HOTKEYS, state="readonly", width=16).pack(side="left", padx=4)

        # ── Save / Cancel ─────────────────────────────────────────────
        btn_row = tk.Frame(self._win, bg=BG)
        btn_row.pack(pady=16)

        tk.Button(btn_row, text="💾  Save & Close", command=self._save,
                  font=F_BTN, bg=BLUE, fg=BG, relief="flat",
                  padx=22, pady=9, cursor="hand2",
                  activebackground="#74c7ec", activeforeground=BG,
                  ).pack(side="left", padx=8)
        tk.Button(btn_row, text="Cancel", command=self._win.destroy,
                  font=F_BODY, bg="#45475a", fg=FG, relief="flat",
                  padx=22, pady=9, cursor="hand2",
                  ).pack(side="left", padx=8)

    # ── Helpers ───────────────────────────────────────────────────────

    def _sec(self, parent, text, font):
        tk.Label(parent, text=text, font=font, bg=BG, fg=BLUE
                 ).pack(anchor="w", pady=(12, 3))

    def _row_frame(self, parent) -> tk.Frame:
        f = tk.Frame(parent, bg=CARD)
        f.pack(fill="x", pady=1)
        return f

    def _entry_row(self, parent, label, var, f_body, f_mono, hide=False):
        row = self._row_frame(parent)
        tk.Label(row, text=label, width=16, anchor="w",
                 font=f_body, bg=CARD, fg=FG).pack(side="left", padx=12, pady=8)
        kw = dict(textvariable=var, width=30, bg=ENTRY, fg=FG,
                  insertbackground=FG, relief="flat", font=f_mono)
        if hide:
            kw["show"] = "•"
        tk.Entry(row, **kw).pack(side="left", padx=4)

    # ── Fetch ─────────────────────────────────────────────────────────

    def _fetch_dg(self):
        state.deepgram_api_key = self._dg_key.get().strip()
        models = self._dg.fetch_models()
        if models:
            self._dg_model_cb["values"] = models
            self._dg_model.set(models[0])
        else:
            messagebox.showwarning("Deepgram", "Could not fetch models.\nCheck your API key.")

    def _fetch_groq(self):
        state.groq_api_key = self._groq_key.get().strip()
        models = self._groq.fetch_models()
        if models:
            self._groq_model_cb["values"] = models
            self._groq_model.set(models[0])
        else:
            messagebox.showwarning("Groq", "Could not fetch models.\nCheck your API key.")

    # ── Save ──────────────────────────────────────────────────────────

    def _save(self):
        old_key    = state.hotkey
        state.deepgram_api_key        = self._dg_key.get().strip()
        state.groq_api_key            = self._groq_key.get().strip()
        state.deepgram_model          = self._dg_model.get()
        state.deepgram_language       = self._lang.get().strip()
        state.groq_model              = self._groq_model.get()
        state.groq_enabled            = self._groq_en.get()
        state.groq_mode               = self._groq_mode.get()
        state.groq_translation_target = self._trans.get().strip()
        state.hotkey                  = self._hotkey.get()
        state.save()

        if state.hotkey != old_key and self._on_hotkey_change:
            self._on_hotkey_change(state.hotkey)

        messagebox.showinfo("Saved", "✅  Settings saved successfully!")
        self._win.destroy()
