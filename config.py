# =============================================================
#  VocalFlow Windows — Central Configuration
#  Edit this file to set your API keys before running.
# =============================================================

# ─── API Keys (hardcoded as required) ────────────────────────
DEEPGRAM_API_KEY = "YOUR_DEEPGRAM_API_KEY_HERE"
GROQ_API_KEY     = "YOUR_GROQ_API_KEY_HERE"

# ─── Hotkey ──────────────────────────────────────────────────
# Options: "right alt", "right ctrl", "caps lock", "right shift", "f9"
DEFAULT_HOTKEY = "right alt"

# ─── Deepgram defaults ───────────────────────────────────────
DEEPGRAM_MODEL    = "nova-2"
DEEPGRAM_LANGUAGE = "en-US"

# ─── Groq defaults ───────────────────────────────────────────
GROQ_MODEL              = "llama3-8b-8192"
GROQ_ENABLED            = False
GROQ_MODE               = "grammar"   # "spelling" | "grammar" | "translation" | "codemix"
GROQ_TRANSLATION_TARGET = "English"

# ─── Audio ───────────────────────────────────────────────────
AUDIO_SAMPLE_RATE = 16000   # Hz  (Deepgram prefers 16 kHz)
AUDIO_CHANNELS    = 1       # mono
AUDIO_CHUNK_MS    = 100     # chunk size sent per callback

# ─── App meta ────────────────────────────────────────────────
APP_NAME         = "VocalFlow"
APP_VERSION      = "1.0.0"
SETTINGS_FILE    = "vocalflow_settings.json"   # saved next to main.py
