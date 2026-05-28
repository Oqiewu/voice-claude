import ctypes
import ctypes.wintypes
import logging
import time

from pynput.keyboard import Controller, Key

logger = logging.getLogger(__name__)

_SETTLE_DELAY = 0.15

_user32   = ctypes.windll.user32
_kernel32 = ctypes.windll.kernel32
_CF_UNICODETEXT = 13
_GMEM_MOVEABLE  = 0x0002


def _copy_to_clipboard(text: str) -> None:
    """Write text to Windows clipboard using ctypes — no subprocess, no hidden window."""
    encoded = text.encode("utf-16-le")
    size    = len(encoded) + 2  # +2 for null terminator

    handle = _kernel32.GlobalAlloc(_GMEM_MOVEABLE, size)
    ptr    = _kernel32.GlobalLock(handle)
    ctypes.memmove(ptr, encoded, len(encoded))
    ctypes.memset(ptr + len(encoded), 0, 2)
    _kernel32.GlobalUnlock(handle)

    _user32.OpenClipboard(0)
    _user32.EmptyClipboard()
    _user32.SetClipboardData(_CF_UNICODETEXT, handle)
    _user32.CloseClipboard()


class TextInjector:
    def __init__(self) -> None:
        self._keyboard = Controller()

    def paste(self, text: str) -> None:
        if not text:
            return
        time.sleep(_SETTLE_DELAY)
        _copy_to_clipboard(text)
        time.sleep(0.05)
        with self._keyboard.pressed(Key.ctrl):
            self._keyboard.press("v")
            self._keyboard.release("v")
        time.sleep(0.05)
        self._keyboard.press(Key.enter)
        self._keyboard.release(Key.enter)
        logger.info("Pasted %d characters and submitted", len(text))
