import logging
import threading

import numpy as np
import sounddevice as sd

from .config import Config

logger = logging.getLogger(__name__)


class AudioRecorder:
    def __init__(self, config: Config) -> None:
        self._config = config
        self._lock = threading.Lock()
        self._chunks: list[np.ndarray] = []
        self._recording = False
        self._stream = sd.InputStream(
            samplerate=config.sample_rate,
            channels=config.channels,
            dtype="float32",
            callback=self._callback,
        )

    def _callback(self, indata: np.ndarray, frames: int, time, status) -> None:
        if status:
            logger.warning("Audio stream status: %s", status)
        with self._lock:
            if self._recording:
                self._chunks.append(indata.copy())

    def start(self) -> None:
        with self._lock:
            self._chunks.clear()
            self._recording = True
        logger.info("Recording started")

    def stop(self) -> np.ndarray:
        with self._lock:
            self._recording = False
            audio = np.concatenate(self._chunks, axis=0).flatten() if self._chunks else np.array([])
        logger.info("Recording stopped, captured %.1f seconds", len(audio) / self._config.sample_rate)
        return audio

    def __enter__(self) -> "AudioRecorder":
        self._stream.start()
        return self

    def __exit__(self, *_) -> None:
        self._stream.stop()
        self._stream.close()
