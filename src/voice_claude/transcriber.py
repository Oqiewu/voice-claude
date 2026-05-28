import logging
import os
import tempfile
import wave

import numpy as np
from faster_whisper import WhisperModel

from .config import Config

logger = logging.getLogger(__name__)


class Transcriber:
    def __init__(self, config: Config) -> None:
        self._config = config
        logger.info("Loading Whisper model '%s'...", config.model_size)
        self._model = WhisperModel(
            config.model_size,
            device=config.device,
            compute_type=config.compute_type,
            local_files_only=True,  # model must be pre-downloaded by installer
        )
        logger.info("Whisper model loaded")

    def transcribe(self, audio: np.ndarray) -> str:
        if audio.size == 0:
            return ""

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            tmp_path = f.name

        try:
            self._write_wav(tmp_path, audio)
            segments, _ = self._model.transcribe(tmp_path, language=self._config.language)
            return " ".join(s.text for s in segments).strip()
        finally:
            os.unlink(tmp_path)

    def _write_wav(self, path: str, audio: np.ndarray) -> None:
        with wave.open(path, "wb") as wf:
            wf.setnchannels(self._config.channels)
            wf.setsampwidth(2)
            wf.setframerate(self._config.sample_rate)
            wf.writeframes((audio * 32767).astype(np.int16).tobytes())
