"""
src/audio_engine.py
Captures microphone audio as raw 16-bit PCM chunks using sounddevice.
"""

import queue
import sys
import os
import numpy as np
import sounddevice as sd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config
from src.app_state import state


class AudioEngine:
    """Opens a mic stream when recording starts; drains it on stop."""

    def __init__(self):
        self._queue: queue.Queue = queue.Queue()
        self._stream = None
        self._active = False

    # ── Public ────────────────────────────────────────────────────────

    def start_recording(self):
        if self._active:
            return
        self._active = True
        self._queue = queue.Queue()   # fresh per recording

        def _cb(indata, frames, time_info, status):
            if status:
                print(f"[Audio] {status}")
            if self._active:
                pcm = (indata[:, 0] * 32767).astype(np.int16)
                self._queue.put(pcm.tobytes())

        block = int(config.AUDIO_SAMPLE_RATE * config.AUDIO_CHUNK_MS / 1000)
        try:
            self._stream = sd.InputStream(
                samplerate=config.AUDIO_SAMPLE_RATE,
                channels=config.AUDIO_CHANNELS,
                dtype="float32",
                blocksize=block,
                callback=_cb,
            )
            self._stream.start()
            state.set_status("🎙️  Recording…")
            print("[Audio] Recording started.")
        except Exception as e:
            self._active = False
            state.set_status(f"❌ Mic error: {e}")
            print(f"[Audio] Stream error: {e}")

    def stop_recording(self) -> bytes:
        """Stop the stream and return all captured PCM as a single bytes object."""
        self._active = False
        if self._stream:
            try:
                self._stream.stop()
                self._stream.close()
            except Exception as e:
                print(f"[Audio] Stop error: {e}")
            self._stream = None

        chunks = []
        while True:
            try:
                chunks.append(self._queue.get_nowait())
            except queue.Empty:
                break

        print(f"[Audio] Stopped. {len(chunks)} chunks captured.")
        state.set_status("⏳ Transcribing…")
        return b"".join(chunks)

    @property
    def is_recording(self) -> bool:
        return self._active
