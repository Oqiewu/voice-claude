import threading
from enum import Enum

from PIL import Image, ImageDraw
import pystray


class State(Enum):
    IDLE        = "#4A90D9"   # blue
    RECORDING   = "#E74C3C"   # red
    PROCESSING  = "#F39C12"   # orange


def _make_icon(color: str) -> Image.Image:
    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # body
    d.ellipse([4, 4, 60, 60], fill=color)
    # microphone shape in white
    d.rounded_rectangle([22, 10, 42, 36], radius=10, fill="white")
    d.arc([14, 28, 50, 48], start=0, end=180, fill="white", width=4)
    d.line([32, 48, 32, 56], fill="white", width=4)
    d.line([22, 56, 42, 56], fill="white", width=4)
    return img


_ICONS = {s: _make_icon(s.value) for s in State}
_TOOLTIPS = {
    State.IDLE:       "voice-claude — idle (ScrollLock to record)",
    State.RECORDING:  "voice-claude — recording...",
    State.PROCESSING: "voice-claude — processing...",
}


class TrayApp:
    def __init__(self, on_quit: callable) -> None:
        self._tray = pystray.Icon(
            name="voice-claude",
            icon=_ICONS[State.IDLE],
            title=_TOOLTIPS[State.IDLE],
            menu=pystray.Menu(
                pystray.MenuItem("voice-claude", None, enabled=False),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Quit", lambda: on_quit()),
            ),
        )

    def set_state(self, state: State) -> None:
        self._tray.icon  = _ICONS[state]
        self._tray.title = _TOOLTIPS[state]

    def run(self) -> None:
        self._tray.run()

    def stop(self) -> None:
        self._tray.stop()
