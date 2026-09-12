import argparse
import time
import camera
import debug
import cv2
import framing
from detector import Detector, parse_detections
from preview import Preview, Overlay
from speech_io import SpeechIO
from argparse import Namespace  # Type hinting for argparse arguments
from cv2.typing import MatLike  # Type hinting for cv2 images and matrices
from enum import StrEnum

# Tuple: ("<flag>", "<help message>")
ARGS = [
    ("--tts", "Test TTS: type text, hear it spoken"),
    ("--stt", "Test STT: speak, see transcript printed"),
    ("--detect", "Test detection: live webcam with YOLO boxes side-by-side"),
    ("--gui", "Show live video with detections and framing guidance"),
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

# Seconds before an unchanged instruction is spoken again, so the user hears
# reassurance without a wall of speech.
REPEAT_SECONDS = 3.0

# Where the framed photograph is written.
OUTPUT_FILE = "capture.jpg"

# Collection of TTS phrases


class Phrases(StrEnum):
    LIST_OBJECTS = "The detected objects were "
    PROMPT_CHOOSE_OBJECT = "Which object would you like to frame?"
    INVALID_RESPONSE = "Invalid response. Try again."
    PROMPT_CHOOSE_REGION = "Choose a region in which to frame the "
    NO_OBJECTS = "I could not detect any objects. Please try again."
    OBJECT_LOST = "I cannot see the "
    FRAMED = "Got it. Taking the picture."
    SAVED = "Picture saved."


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


def guide_to_frame(preview: Preview,
                   detector: Detector,
                   sio: SpeechIO,
                   label: str,
                   region_name: str) -> MatLike | None:
    """Speak movement instructions until `label` sits inside `region_name`.

    Runs detection continuously rather than capturing, moving, and recapturing:
    the user hears a correction the moment the camera drifts. Returns the frame
    the object was framed in, or None if the user quit the preview window.
    """
    last_said: str | None = None
    last_time = 0.0

    while not preview.quit_requested.is_set():
        frame = preview.latest()

        # Read the size from the frame itself: the webcam may not have given
        # us the resolution we asked for.
        height, width = frame.shape[:2]
        region = framing.region_bbox(region_name, width, height)

        # Several cups may be in view; track the one YOLO is surest of.
        matches = [detection
                   for detection in parse_detections(detector.detect(frame))
                   if detection[0] == label]
        box = max(matches, key=lambda d: d[2])[1] if matches else None

        if box is None:
            # Motion blur routinely costs a detection or two mid-turn.
            instruction = Phrases.OBJECT_LOST + label
        else:
            instruction = framing.guidance(box, region, width, height)

        preview.set_overlay(Overlay(
            boxes=[(box, label)] if box is not None else [],
            region=region,
            text=instruction or "Framed"))

        if instruction is None:
            return frame

        # Speak only when the advice changes, or periodically to reassure.
        now = time.monotonic()
        if instruction != last_said or now - last_time > REPEAT_SECONDS:
            sio.speak(instruction)
            last_said, last_time = instruction, now

    return None


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

    detector: Detector = Detector()

    # The preview thread owns the camera for the whole run and, with --gui,
    # keeps live video on screen while this thread blocks on speech.
    cap = camera.open_camera()
    preview = Preview(cap, show=args.gui)
    preview.start()
    try:
        # 1. Capture image
        frame = preview.latest()

        # 2. Detect objects
        detections = parse_detections(detector.detect(frame))
        preview.set_overlay(Overlay(
            boxes=[(box, label) for label, box, _ in detections]))

        # 3. List detected objects, deduplicated but kept in detection order
        objects = list(dict.fromkeys(label for label, _, _ in detections))
        if not objects:
            sio.speak(Phrases.NO_OBJECTS)
            return
        sio.speak(Phrases.LIST_OBJECTS + ", ".join(objects))

        # 4. Ask object choice
        sio.speak(Phrases.PROMPT_CHOOSE_OBJECT)

        # 5. Get user object choice
        chosen_object = sio.make_choice(
            choices=objects, invalid_response=Phrases.INVALID_RESPONSE)

        # 6. Ask object framing
        sio.speak(Phrases.PROMPT_CHOOSE_REGION +
                  chosen_object + ": " + ", ".join(REGIONS))

        # 7. Get user framing region choice
        chosen_region = sio.make_choice(
            choices=REGIONS, invalid_response=Phrases.INVALID_RESPONSE)
        sio.speak(f"You chose: {chosen_region}")

        # 8-12. Guide the user until the object sits in the chosen region.
        # Steps 8 through 12 all live inside this loop: it measures coverage,
        # picks a direction, speaks it, and re-detects on the next frame.
        framed = guide_to_frame(preview, detector, sio,
                                chosen_object, chosen_region)
        if framed is None:  # User quit the preview window
            return

        # 13. Capture image (the frame the object was framed in)
        sio.speak(Phrases.FRAMED)
        cv2.imwrite(OUTPUT_FILE, framed)
        sio.speak(Phrases.SAVED)
        print(f"Saved {OUTPUT_FILE}")
    finally:
        preview.stop()
        cap.release()


if __name__ == "__main__":
    main()
