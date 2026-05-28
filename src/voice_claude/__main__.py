import logging
import threading

from pynput import keyboard

from .audio import AudioRecorder
from .config import Config
from .injector import TextInjector
from .transcriber import Transcriber

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def main() -> None:
    config = Config()
    recorder = AudioRecorder(config)
    transcriber = Transcriber(config)
    injector = TextInjector()

    is_recording = False

    def handle_release(key: keyboard.Key) -> None:
        nonlocal is_recording
        if key != config.hotkey or not is_recording:
            return
        is_recording = False
        audio = recorder.stop()

        def _process() -> None:
            text = transcriber.transcribe(audio)
            if text:
                logger.info(">> %s", text)
                injector.paste(text)
            else:
                logger.info("(nothing recognized)")

        threading.Thread(target=_process, daemon=True).start()

    def handle_press(key: keyboard.Key) -> None:
        nonlocal is_recording
        if key == config.hotkey and not is_recording:
            is_recording = True
            recorder.start()

    logger.info("Ready. Hold ScrollLock and speak. Ctrl+C to exit.")

    with recorder:
        with keyboard.Listener(on_press=handle_press, on_release=handle_release) as listener:
            try:
                listener.join()
            except KeyboardInterrupt:
                logger.info("Exiting.")


if __name__ == "__main__":
    main()
