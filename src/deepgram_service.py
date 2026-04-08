"""
src/deepgram_service.py
Deepgram REST transcription + account balance fetching.
"""

import struct
import sys
import os
import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config
from src.app_state import state


class DeepgramService:
    BASE = "https://api.deepgram.com/v1"

    # ── Auth header ───────────────────────────────────────────────────

    def _auth(self) -> dict:
        return {"Authorization": f"Token {state.deepgram_api_key}"}

    # ── Transcription ─────────────────────────────────────────────────

    def transcribe(self, pcm_bytes: bytes) -> str:
        """Send PCM audio to Deepgram and return the transcript string."""
        if not pcm_bytes:
            return ""
        key = state.deepgram_api_key
        if not key or key.startswith("YOUR_"):
            state.set_status("❌ Deepgram key missing — edit config.py")
            return ""

        wav = self._pcm_to_wav(pcm_bytes)
        headers = {**self._auth(), "Content-Type": "audio/wav"}
        params = {
            "model":        state.deepgram_model,
            "language":     state.deepgram_language,
            "smart_format": "true",
            "punctuate":    "true",
        }
        try:
            r = requests.post(
                f"{self.BASE}/listen",
                headers=headers,
                params=params,
                data=wav,
                timeout=30,
            )
            r.raise_for_status()
            channels = r.json().get("results", {}).get("channels", [])
            if channels:
                alts = channels[0].get("alternatives", [])
                if alts:
                    text = alts[0].get("transcript", "").strip()
                    print(f"[Deepgram] transcript: {text!r}")
                    return text
            return ""
        except requests.HTTPError as e:
            state.set_status(f"❌ Deepgram HTTP {e.response.status_code}")
            print(f"[Deepgram] HTTP error: {e}")
        except Exception as e:
            state.set_status(f"❌ Deepgram: {e}")
            print(f"[Deepgram] error: {e}")
        return ""

    # ── Balance ───────────────────────────────────────────────────────

    def get_balance(self) -> dict:
        """
        Return dict:
          success → {"balance": float, "currency": str, "project": str}
          failure → {"error": str}
        """
        key = state.deepgram_api_key
        if not key or key.startswith("YOUR_"):
            return {"error": "API key not configured"}
        try:
            # 1. list projects
            pr = requests.get(f"{self.BASE}/projects", headers=self._auth(), timeout=10)
            pr.raise_for_status()
            projects = pr.json().get("projects", [])
            if not projects:
                return {"error": "No projects found"}
            pid   = projects[0]["project_id"]
            pname = projects[0].get("name", pid)

            # 2. fetch balance for first project
            br = requests.get(
                f"{self.BASE}/projects/{pid}/balances",
                headers=self._auth(), timeout=10,
            )
            br.raise_for_status()
            balances = br.json().get("balances", [])
            if balances:
                b = balances[0]
                return {
                    "balance":  float(b.get("amount", 0)),
                    "currency": b.get("units", "USD"),
                    "project":  pname,
                }
            return {"error": "No balance records returned"}
        except requests.HTTPError as e:
            return {"error": f"HTTP {e.response.status_code}"}
        except Exception as e:
            return {"error": str(e)}

    # ── Models ────────────────────────────────────────────────────────

    def fetch_models(self) -> list[str]:
        key = state.deepgram_api_key
        if not key or key.startswith("YOUR_"):
            return ["nova-2", "nova", "enhanced", "base"]
        try:
            r = requests.get(f"{self.BASE}/models", headers=self._auth(), timeout=10)
            r.raise_for_status()
            stt = r.json().get("stt", [])
            return [m.get("name") or m.get("canonical_name", "") for m in stt if m.get("name")]
        except Exception as e:
            print(f"[Deepgram] fetch_models: {e}")
            return ["nova-2", "nova", "enhanced", "base"]

    # ── PCM → WAV ─────────────────────────────────────────────────────

    @staticmethod
    def _pcm_to_wav(pcm: bytes) -> bytes:
        sr   = config.AUDIO_SAMPLE_RATE
        ch   = config.AUDIO_CHANNELS
        bps  = 16
        br   = sr * ch * bps // 8
        ba   = ch * bps // 8
        dlen = len(pcm)
        hdr = struct.pack(
            "<4sI4s4sIHHIIHH4sI",
            b"RIFF", 36 + dlen, b"WAVE",
            b"fmt ", 16, 1, ch, sr, br, ba, bps,
            b"data", dlen,
        )
        return hdr + pcm
