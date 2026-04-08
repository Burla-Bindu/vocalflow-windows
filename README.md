# VocalFlow for Windows

> **Windows port of [VocalFlow](https://github.com/Vocallabsai/vocalflow)** — a lightweight system-tray dictation app.  
> Hold a key → speak → release → text appears at your cursor, in any app.

---

## ✨ Features

| # | Feature | Details |
|---|---------|---------|
| ✅ | **Hold-to-record hotkey** | Right Alt (default) — configurable |
| ✅ | **Real-time transcription** | Deepgram REST API (nova-2 model) |
| ✅ | **Works in any app** | Text injected via Ctrl+V paste |
| ✅ | **Groq post-processing** | Spelling · Grammar · Translation · Code-mix |
| ✅ | **System tray app** | Lives in taskbar, no window clutter |
| ⭐ | **API Balance Dashboard** | Shows Deepgram credit balance + Groq key status *(extra feature)* |
| ✅ | **Settings UI** | Tkinter panel — model, language, hotkey, post-processing |
| ✅ | **Config file** | All keys hardcoded in `config.py` for easy testing |

---

## 📁 Project Structure

```
vocalflow-windows/
│
├── config.py                  ← 🔑 API keys & defaults — EDIT THIS FIRST
├── main.py                    ← Entry point
│
├── src/
│   ├── __init__.py
│   ├── app_state.py           ← Shared state + settings persistence
│   ├── audio_engine.py        ← Microphone capture (sounddevice)
│   ├── deepgram_service.py    ← Deepgram transcription + balance API
│   ├── groq_service.py        ← Groq post-processing + key validation
│   ├── text_injector.py       ← Clipboard-based Ctrl+V injection
│   ├── hotkey_manager.py      ← Global hold-to-record hotkey
│   ├── tray_controller.py     ← System-tray icon & menu
│   ├── settings_window.py     ← Settings GUI (Tkinter)
│   └── balance_window.py      ← ⭐ API Balance dashboard (extra feature)
│
├── requirements.txt           ← Python dependencies
├── setup.bat                  ← One-click install
├── run.bat                    ← One-click launch (as Admin)
└── README.md                  ← This file
```

---

## 🖥️ Requirements

| Requirement | Details |
|-------------|---------|
| OS | Windows 10 or Windows 11 |
| Python | 3.10 or newer |
| Microphone | Any — USB, built-in, headset |
| Deepgram API key | Free tier — $200 credits on signup |
| Groq API key | Optional — free tier available |

---

## 🚀 Quick Start (3 Steps)

### Step 1 — Add your API keys

Open **`config.py`** in any text editor and fill in:

```python
DEEPGRAM_API_KEY = "your_deepgram_key_here"   # required
GROQ_API_KEY     = "your_groq_key_here"        # optional
```

Get keys here:
- **Deepgram** (free): https://console.deepgram.com/signup
- **Groq** (free): https://console.groq.com

---

### Step 2 — Install dependencies

Double-click **`setup.bat`**

This installs all Python packages from `requirements.txt` automatically.

---

### Step 3 — Run the app

Double-click **`run.bat`**

> The app requests **Administrator** privileges automatically (required for global hotkey detection). Click Yes on the UAC prompt.

Look for the 🎙️ **microphone icon** in your system tray (bottom-right corner).

---

## 🎮 How to Use

| Action | What happens |
|--------|-------------|
| **Hold `Right Alt`** | Recording starts (icon turns 🔴 red) |
| **Speak** | Audio is captured |
| **Release `Right Alt`** | Audio → Deepgram → text pasted at cursor |
| **Right-click tray icon** | Opens menu |

### Tray Menu

| Item | Action |
|------|--------|
| 📊 **API Balances** | Opens balance dashboard (Deepgram + Groq) |
| ⚙️ **Settings** | Configure keys, model, hotkey, post-processing |
| ❓ **About** | App info |
| 🚪 **Quit** | Exit |

---

## 💳 API Balance Dashboard ⭐ (Extra Feature)

Right-click tray → **API Balances**

| Panel | Shows |
|-------|-------|
| 🎙️ Deepgram | Current USD credit balance + project name |
| ⚡ Groq | Key validity status + number of available models |

Green dot = connected ✅ · Red dot = error ❌ · Yellow dot = loading ⏳

Click **Refresh** at any time to reload live data.

---

## ⚙️ Settings Panel

Open from tray → **Settings**

| Setting | Description |
|---------|-------------|
| Deepgram API Key | Overrides `config.py` at runtime |
| Deepgram Model | `nova-2` (recommended), `nova`, `enhanced`, `base` |
| Language | `en-US`, `hi`, `es`, `fr`, etc. |
| Groq API Key | Optional — for post-processing |
| Groq Model | `llama3-8b-8192` (default), `llama3-70b-8192`, etc. |
| Post-processing | Enable/disable Groq |
| Mode | `spelling` · `grammar` · `translation` · `codemix` |
| Translate to | Target language for translation mode |
| Hotkey | Which key to hold — Right Alt, Right Ctrl, Caps Lock… |

Changes are saved to `vocalflow_settings.json` and survive restarts.

---

## 🔧 Troubleshooting

| Problem | Fix |
|---------|-----|
| Hotkey not working | Make sure you launched via `run.bat` (runs as Admin) |
| Mic not capturing | Check microphone permissions: Windows Settings → Privacy → Microphone |
| Deepgram 401 error | Check `DEEPGRAM_API_KEY` in `config.py` |
| Text not pasting | Click into the target app *before* speaking; cursor must be in a text field |
| `ModuleNotFoundError` | Run `setup.bat` first |
| App won't start | Run `python main.py` in a terminal to see the full error |

---

## 🏗️ How It Works

```
Hold hotkey
    │
    ▼
AudioEngine            sounddevice captures mic → raw PCM
    │
Release hotkey
    │
    ▼
DeepgramService        PCM wrapped in WAV → POST /v1/listen → transcript
    │
    ▼  (if Groq enabled)
GroqService            transcript → LLM → polished text
    │
    ▼
TextInjector           copy to clipboard → Ctrl+V → text at cursor
```

---

## 📦 Dependencies

| Package | Purpose |
|---------|---------|
| `sounddevice` | Microphone capture |
| `numpy` | PCM float→int16 conversion |
| `requests` | Deepgram + Groq REST calls |
| `pystray` | Windows system-tray icon |
| `Pillow` | Tray icon drawing |
| `keyboard` | Global hotkey detection |
| `pyperclip` | Clipboard read/write |
| `pyautogui` | Ctrl+V simulation |

All built-in (Tkinter, threading, json, struct) — no extra install needed.

---

## 📄 License

MIT — same as the original [VocalFlow macOS app](https://github.com/Vocallabsai/vocalflow).

---

## 🙏 Credits

- **Original macOS app**: [Vocallabsai/vocalflow](https://github.com/Vocallabsai/vocalflow)
- **Transcription**: [Deepgram](https://deepgram.com)
- **LLM post-processing**: [Groq](https://groq.com)

# VocalFlow Windows
A real-time voice-to-text Windows tray application using Deepgram speech recognition and Groq AI post-processing.

## Setup Instructions
1. Download the project ZIP
2. Extract the folder
3. Open config.py
4. Add your Deepgram and Groq API keys
5. Run setup.bat
6. Run run.bat as Administrator
7. Hold Right Alt and speak to type
