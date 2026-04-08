"""
src/balance_window.py
─────────────────────
EXTRA FEATURE: API Balance Dashboard
Shows Deepgram credit balance and Groq key status in a dedicated window.
Auto-refreshes on open; manual Refresh button included.
"""

import threading
import tkinter as tk
from tkinter import font as tkf
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.deepgram_service import DeepgramService
from src.groq_service import GroqService

# ── Palette (matches settings window) ────────────────────────────────
BG       = "#1e1e2e"
CARD     = "#2a2a3e"
BORDER   = "#3d3d5c"
FG       = "#cdd6f4"
MUTED    = "#6c7086"
GREEN    = "#a6e3a1"
RED      = "#f38ba8"
YELLOW   = "#f9e2af"
BLUE     = "#89b4fa"
PURPLE   = "#cba6f7"


class BalanceWindow:
    """Toplevel window showing live API balances."""

    def __init__(self):
        self._dg   = DeepgramService()
        self._groq = GroqService()
        self._win  = None

    def show(self):
        if self._win and self._win.winfo_exists():
            self._win.lift()
            self._win.focus_force()
            return
        self._build()
        self._refresh()   # auto-load on open

    # ── Build UI ──────────────────────────────────────────────────────

    def _build(self):
        self._win = tk.Toplevel()
        self._win.title("API Balances — VocalFlow")
        self._win.geometry("460x400")
        self._win.resizable(False, False)
        self._win.configure(bg=BG)
        self._win.grab_set()

        F_TITLE  = tkf.Font(family="Segoe UI", size=14, weight="bold")
        F_CARD_H = tkf.Font(family="Segoe UI", size=11, weight="bold")
        F_BODY   = tkf.Font(family="Segoe UI", size=10)
        F_AMOUNT = tkf.Font(family="Consolas",  size=16, weight="bold")
        F_SMALL  = tkf.Font(family="Segoe UI", size=9)
        F_BTN    = tkf.Font(family="Segoe UI", size=10, weight="bold")

        # ── Header ────────────────────────────────────────────────────
        tk.Label(self._win, text="💳  API Balances",
                 font=F_TITLE, bg=BG, fg=FG).pack(pady=(22, 2))
        tk.Label(self._win,
                 text="Live status for your Deepgram and Groq accounts",
                 font=F_SMALL, bg=BG, fg=MUTED).pack(pady=(0, 16))

        # ── Deepgram card ─────────────────────────────────────────────
        dg_card = self._card(self._win)

        dg_top = tk.Frame(dg_card, bg=CARD)
        dg_top.pack(fill="x", padx=18, pady=(14, 0))
        tk.Label(dg_top, text="🎙️  Deepgram",
                 font=F_CARD_H, bg=CARD, fg=BLUE).pack(side="left")
        self._dg_dot = tk.Label(dg_top, text="●", font=F_BODY, bg=CARD, fg=MUTED)
        self._dg_dot.pack(side="right")

        self._dg_amount = tk.StringVar(value="—")
        tk.Label(dg_card, textvariable=self._dg_amount,
                 font=F_AMOUNT, bg=CARD, fg=GREEN).pack(padx=18, pady=(6, 0))

        self._dg_detail = tk.StringVar(value="Press Refresh to load")
        tk.Label(dg_card, textvariable=self._dg_detail,
                 font=F_SMALL, bg=CARD, fg=MUTED).pack(padx=18, pady=(2, 16))

        # ── Groq card ─────────────────────────────────────────────────
        gq_card = self._card(self._win)

        gq_top = tk.Frame(gq_card, bg=CARD)
        gq_top.pack(fill="x", padx=18, pady=(14, 0))
        tk.Label(gq_top, text="⚡  Groq",
                 font=F_CARD_H, bg=CARD, fg=PURPLE).pack(side="left")
        self._gq_dot = tk.Label(gq_top, text="●", font=F_BODY, bg=CARD, fg=MUTED)
        self._gq_dot.pack(side="right")

        self._gq_amount = tk.StringVar(value="—")
        tk.Label(gq_card, textvariable=self._gq_amount,
                 font=F_AMOUNT, bg=CARD, fg=GREEN).pack(padx=18, pady=(6, 0))

        self._gq_detail = tk.StringVar(value="Press Refresh to load")
        tk.Label(gq_card, textvariable=self._gq_detail,
                 font=F_SMALL, bg=CARD, fg=MUTED).pack(padx=18, pady=(2, 16))

        # ── Buttons ───────────────────────────────────────────────────
        btn_row = tk.Frame(self._win, bg=BG)
        btn_row.pack(pady=14)

        self._refresh_btn = tk.Button(
            btn_row, text="🔄  Refresh", command=self._refresh,
            font=F_BTN, bg=BLUE, fg=BG, relief="flat",
            padx=22, pady=9, cursor="hand2",
            activebackground="#74c7ec", activeforeground=BG,
        )
        self._refresh_btn.pack(side="left", padx=8)

        tk.Button(
            btn_row, text="Close", command=self._win.destroy,
            font=F_BODY, bg="#45475a", fg=FG, relief="flat",
            padx=22, pady=9, cursor="hand2",
            activebackground="#585b70", activeforeground=FG,
        ).pack(side="left", padx=8)

    # ── Card helper ───────────────────────────────────────────────────

    def _card(self, parent) -> tk.Frame:
        outer = tk.Frame(parent, bg=BORDER)
        outer.pack(fill="x", padx=24, pady=(0, 12))
        inner = tk.Frame(outer, bg=CARD)
        inner.pack(fill="both", expand=True, padx=1, pady=1)
        return inner

    # ── Refresh ───────────────────────────────────────────────────────

    def _refresh(self):
        if not (self._win and self._win.winfo_exists()):
            return
        self._refresh_btn.config(state="disabled", text="⏳ Loading…")
        self._dg_dot.config(fg=YELLOW)
        self._gq_dot.config(fg=YELLOW)
        self._dg_amount.set("Fetching…")
        self._gq_amount.set("Fetching…")
        self._dg_detail.set("")
        self._gq_detail.set("")

        threading.Thread(target=self._load_dg,   daemon=True).start()
        threading.Thread(target=self._load_groq, daemon=True).start()

        # re-enable after 4 s
        if self._win and self._win.winfo_exists():
            self._win.after(4000, lambda: self._refresh_btn.config(
                state="normal", text="🔄  Refresh"))

    def _load_dg(self):
        result = self._dg.get_balance()
        if self._win and self._win.winfo_exists():
            self._win.after(0, lambda: self._show_dg(result))

    def _load_groq(self):
        result = self._groq.get_balance()
        if self._win and self._win.winfo_exists():
            self._win.after(0, lambda: self._show_groq(result))

    def _show_dg(self, r: dict):
        if "error" in r:
            self._dg_amount.set("Error")
            self._dg_detail.set(r["error"])
            self._dg_dot.config(fg=RED)
        else:
            bal  = r.get("balance", 0)
            curr = r.get("currency", "USD")
            proj = r.get("project", "")
            self._dg_amount.set(f"${bal:.4f} {curr}")
            self._dg_detail.set(f"Project: {proj}")
            self._dg_dot.config(fg=GREEN)

    def _show_groq(self, r: dict):
        if "error" in r:
            self._gq_amount.set("Error")
            self._gq_detail.set(r["error"])
            self._gq_dot.config(fg=RED)
        else:
            self._gq_amount.set(r.get("status", "Free Tier"))
            self._gq_detail.set(r.get("note", ""))
            self._gq_dot.config(fg=GREEN)
