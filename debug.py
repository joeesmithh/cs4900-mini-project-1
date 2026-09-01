from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from speech_io import SpeechIO


def debug_tts(sio: SpeechIO) -> None:
    """Type text at the prompt; SpeechIO speaks it aloud. Ctrl+C to quit."""
    print("TTS debug (type text and press Enter to hear it spoken. Ctrl+C to quit.)")
    try:
        while True:
            text = input("> ").strip()
            if text:
                sio.speak(text)
    except KeyboardInterrupt:
        print("\nExiting TTS debug.")


def debug_stt(sio: SpeechIO) -> None:
    """Speak into the microphone; transcription is printed to stdout. Ctrl+C to quit."""
    print("STT debug (speak into your microphone. Ctrl+C to quit.)")
    try:
        while True:
            print("Listening...")
            result = sio.listen()
            if result:
                print(f"Heard: {result}")
            else:
                print("(nothing recognized)")
    except KeyboardInterrupt:
        print("\nExiting STT debug.")
