import logging
import time

import pyperclip
from pynput.keyboard import Controller, Key

logger = logging.getLogger(__name__)

_SETTLE_DELAY = 0.15  # seconds to wait after key release before pasting


class TextInjector:
    def __init__(self) -> None:
        self._keyboard = Controller()

    def paste(self, text: str) -> None:
        if not text:
            return
        time.sleep(_SETTLE_DELAY)
        pyperclip.copy(text)
        with self._keyboard.pressed(Key.ctrl):
            self._keyboard.press("v")
            self._keyboard.release("v")
        logger.info("Pasted %d characters", len(text))
