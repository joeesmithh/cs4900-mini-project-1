import argparse
import camera
import debug
import cv2
from detector import Detector
from speech_io import SpeechIO
from argparse import Namespace  # Type hinting for argparse arguments
from cv2.typing import MatLike  # Type hinting for cv2 images and matrices
from enum import StrEnum

# Tuple: ("<flag>", "<help message>")
ARGS = [
    ("--tts", "Test TTS: type text, hear it spoken"),
    ("--stt", "Test STT: speak, see transcript printed"),
    ("--detect", "Test detection: live webcam with YOLO boxes side-by-side"),
    ("--gui", "Visualize the capture and detections side-by-side"),
    ("--voices", "Listen to pyttsx3 voices")
]

# Screen regions
REGIONS = [
    "top left",
    "top right",
    "bottom left",
    "bottom right",
    "center"
]

# Collection of TTS phrases


class Phrases(StrEnum):
    LIST_OBJECTS = "The detected objects were "
    PROMPT_CHOOSE_OBJECT = "Which object would you like to frame?"
    INVALID_RESPONSE = "Invalid response. Try again."
    PROMPT_CHOOSE_REGION = "Choose a region in which to frame the "


def get_args() -> Namespace:
    """Populate argument parser namespace.s"""
    parser = argparse.ArgumentParser(
        description="CS 4900 Camera App for Visually Impaired")
    group = parser.add_mutually_exclusive_group()
    for arg, help in ARGS:
        group.add_argument(arg,
                           action="store_true",
                           help=help)
    parser.add_argument("--voice",
                        type=int,
                        default=1,
                        help="pyttsx3 voice index for TTS output (see --voices)")
    return parser.parse_args()


def main() -> None:

    # Debug
    # -------------------------------------------------------------------------

    # Debug modes: each runs in isolation and skips the main pipeline.
    args: Namespace = get_args()

    if args.detect:
        debug.debug_detect(Detector())
        return

    sio: SpeechIO = SpeechIO(voice_index=args.voice)
    if args.tts or args.stt or args.voices:
        if args.tts:
            debug.debug_tts(sio)
        elif args.stt:
            debug.debug_stt(sio)
        elif args.voices:
            sio.list_voices()
        return

    # Main pipeline
    # -------------------------------------------------------------------------

    # 1. Capture image

    # 2. Detect objects

    # 3. List detected objects
    objects = ["apple", "banana", "cup"]  # Placeholder detection list
    sio.speak(Phrases.LIST_OBJECTS + ", ".join(objects))

    # 4. Ask object choice
    sio.speak(Phrases.PROMPT_CHOOSE_OBJECT)

    # 5. Get user object choice
    result = sio.make_choice(choices=objects,
                             invalid_response=Phrases.INVALID_RESPONSE)

    # 6. Ask object framing
    sio.speak(Phrases.PROMPT_CHOOSE_REGION +
              result + ": " + ", ".join(REGIONS))

    # 7. Get user framing region choice
    result = sio.make_choice(choices=REGIONS,
                             invalid_response=Phrases.INVALID_RESPONSE)
    sio.speak(f"You chose: {result}")

    # TODO: 8. Calculate object area % in frame
    # TODO: 9. Calculate camera movement direction
    # TODO: 10. Instruct user where to move camera
    # TODO: 11. Wait for camera movement
    # TODO: 12. Wait for camera stationary
    # TODO: 13. Capture Image
    # TODO: 14. Detect objects
    # TODO: 15. Is object still in scene?


if __name__ == "__main__":
    main()
