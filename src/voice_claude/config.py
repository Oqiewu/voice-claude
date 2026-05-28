from dataclasses import dataclass
from pathlib import Path

from pynput.keyboard import Key

LOG_PATH = Path.home() / "AppData" / "Local" / "voice-claude" / "voice-claude.log"


@dataclass(frozen=True)
class Config:
    hotkey: Key = Key.scroll_lock
    sample_rate: int = 16000
    channels: int = 1
    language: str = "ru"        # "ru" | "en" | None for auto-detect
    model_size: str = "base"    # tiny | base | small | medium
    device: str = "cpu"
    compute_type: str = "int8"
