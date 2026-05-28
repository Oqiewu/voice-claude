import logging
import os
import threading

os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")
os.environ.setdefault("HF_HUB_VERBOSITY", "error")

from pynput import keyboard

from .audio import AudioRecorder
from .config import Config, LOG_PATH
from .injector import TextInjector
from .transcriber import Transcriber
from .tray import State, TrayApp

LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(message)s",
    datefmt="%H:%M:%S",
    handlers=[logging.FileHandler(LOG_PATH, encoding="utf-8")],
)
logger = logging.getLogger(__name__)


def main() -> None:
    config     = Config()
    recorder   = AudioRecorder(config)
    transcriber = Transcriber(config)
    injector   = TextInjector()
    tray       = TrayApp(on_quit=lambda: _shutdown())

    is_recording = False
    shutdown_event = threading.Event()

    def _shutdown() -> None:
        shutdown_event.set()
        tray.stop()

    def handle_press(key: keyboard.Key) -> None:
        nonlocal is_recording
        if key == config.hotkey and not is_recording:
            is_recording = True
            recorder.start()
            tray.set_state(State.RECORDING)
            logger.info("Recording started")

    def handle_release(key: keyboard.Key) -> None:
        nonlocal is_recording
        if key != config.hotkey or not is_recording:
            return
        is_recording = False
        audio = recorder.stop()
        tray.set_state(State.PROCESSING)

        def _process() -> None:
            text = transcriber.transcribe(audio)
            if text:
                logger.info(">> %s", text)
                injector.paste(text)
            else:
                logger.info("(nothing recognized)")
            tray.set_state(State.IDLE)

        threading.Thread(target=_process, daemon=True).start()

    logger.info("voice-claude started")

    kb_listener = keyboard.Listener(on_press=handle_press, on_release=handle_release)
    kb_listener.start()

    with recorder:
        tray.run()  # blocks until Quit clicked

    kb_listener.stop()
    logger.info("voice-claude stopped")


if __name__ == "__main__":
    main()
