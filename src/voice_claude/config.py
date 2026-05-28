from dataclasses import dataclass

from pynput.keyboard import Key


@dataclass(frozen=True)
class Config:
    hotkey: Key = Key.scroll_lock
    sample_rate: int = 16000
    channels: int = 1
    language: str = "ru"        # "ru" | "en" | None for auto-detect
    model_size: str = "base"    # tiny | base | small | medium
    device: str = "cpu"
    compute_type: str = "int8"
