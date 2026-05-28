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


def _copy_to_clipboard(text: str) -> bool:
    """Write text to Windows clipboard. Returns False if clipboard is busy."""
    encoded = text.encode("utf-16-le")
    size    = len(encoded) + 2

    handle = _kernel32.GlobalAlloc(_GMEM_MOVEABLE, size)
    if not handle:
        return False
    ptr = _kernel32.GlobalLock(handle)
    ctypes.memmove(ptr, encoded, len(encoded))
    ctypes.memset(ptr + len(encoded), 0, 2)
    _kernel32.GlobalUnlock(handle)

    for _ in range(5):          # retry up to 5 times if clipboard is busy
        if _user32.OpenClipboard(0):
            _user32.EmptyClipboard()
            _user32.SetClipboardData(_CF_UNICODETEXT, handle)
            _user32.CloseClipboard()
            return True
        time.sleep(0.05)

    _kernel32.GlobalFree(handle)
    return False


class TextInjector:
    def __init__(self) -> None:
        self._keyboard = Controller()

    def paste(self, text: str) -> None:
        if not text:
            return
        try:
            time.sleep(_SETTLE_DELAY)
            if not _copy_to_clipboard(text):
                logger.error("Clipboard busy — paste skipped")
                return
            time.sleep(0.05)
            self._keyboard.press(Key.ctrl)
            self._keyboard.press("v")
            self._keyboard.release("v")
            self._keyboard.release(Key.ctrl)
            time.sleep(0.05)
            self._keyboard.press(Key.enter)
            self._keyboard.release(Key.enter)
            logger.info("Pasted %d characters and submitted", len(text))
        except Exception:
            logger.exception("paste() failed")
