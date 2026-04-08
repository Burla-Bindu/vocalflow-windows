"""
src/groq_service.py
Groq LLM post-processing (spelling / grammar / translation / codemix)
and account key-validation / model listing used by the balance panel.
"""

import sys
import os
import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.app_state import state


class GroqService:
    BASE = "https://api.groq.com/openai/v1"

    def _auth(self) -> dict:
        return {
            "Authorization": f"Bearer {state.groq_api_key}",
            "Content-Type":  "application/json",
        }

    # ── Post-processing ───────────────────────────────────────────────

    def process(self, text: str) -> str:
        """Run the configured post-processing on `text`; returns original on error."""
        if not text.strip():
            return text
        key = state.groq_api_key
        if not key or key.startswith("YOUR_"):
            state.set_status("⚠️ Groq key missing — skipping post-processing")
            return text

        payload = {
            "model": state.groq_model,
            "messages": [
                {"role": "system", "content": self._system_prompt()},
                {"role": "user",   "content": text},
            ],
            "max_tokens":  512,
            "temperature": 0.1,
        }
        try:
            r = requests.post(
                f"{self.BASE}/chat/completions",
                headers=self._auth(),
                json=payload,
                timeout=15,
            )
            r.raise_for_status()
            result = r.json()["choices"][0]["message"]["content"].strip()
            print(f"[Groq] processed: {result!r}")
            return result
        except requests.HTTPError as e:
            print(f"[Groq] HTTP error: {e}")
        except Exception as e:
            print(f"[Groq] error: {e}")
        return text

    def _system_prompt(self) -> str:
        target = state.groq_translation_target
        return {
            "spelling": (
                "Fix only spelling mistakes in the user's text. "
                "Return ONLY the corrected text—no explanation, no quotes."
            ),
            "grammar": (
                "Fix grammar and spelling in the user's text. "
                "Return ONLY the corrected text—no explanation, no quotes."
            ),
            "translation": (
                f"Translate the user's text into {target}. "
                "Return ONLY the translation—no explanation, no quotes."
            ),
            "codemix": (
                "The user is speaking in a code-mixed language (e.g. Hinglish, Tanglish). "
                "Transliterate and clean it into fluent English. "
                "Return ONLY the result—no explanation, no quotes."
            ),
        }.get(state.groq_mode, "Return the text as-is.")

    # ── Balance / key validation ───────────────────────────────────────

    def get_balance(self) -> dict:
        """
        Groq has no public billing API; we validate the key by listing models.
        Returns dict with "status", "note", "models" or "error".
        """
        key = state.groq_api_key
        if not key or key.startswith("YOUR_"):
            return {"error": "API key not configured"}
        try:
            r = requests.get(f"{self.BASE}/models", headers=self._auth(), timeout=10)
            if r.status_code == 401:
                return {"error": "Invalid API key (401 Unauthorized)"}
            r.raise_for_status()
            models = [m["id"] for m in r.json().get("data", [])]
            return {
                "status": "✅  Key valid",
                "note":   f"{len(models)} models available",
                "models": models,
            }
        except requests.HTTPError as e:
            return {"error": f"HTTP {e.response.status_code}"}
        except Exception as e:
            return {"error": str(e)}

    # ── Model list ────────────────────────────────────────────────────

    def fetch_models(self) -> list[str]:
        key = state.groq_api_key
        if not key or key.startswith("YOUR_"):
            return ["llama3-8b-8192", "llama3-70b-8192", "mixtral-8x7b-32768"]
        try:
            r = requests.get(f"{self.BASE}/models", headers=self._auth(), timeout=10)
            r.raise_for_status()
            return [m["id"] for m in r.json().get("data", [])]
        except Exception as e:
            print(f"[Groq] fetch_models: {e}")
            return ["llama3-8b-8192", "llama3-70b-8192", "mixtral-8x7b-32768"]
