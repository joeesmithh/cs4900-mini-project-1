import argparse
import time
import debug
import cv2
import overlays
import geometry
from datetime import datetime
from pathlib import Path
from detector import Detector, Detection
from speech_io import SpeechIO
from argparse import Namespace  # Type hinting for argparse arguments
from cv2.typing import MatLike  # Type hinting for cv2 images and matrices
from enum import StrEnum
from camera import Camera

# Tuple: ("<flag>", "<help message>")
ARGS = [
    ("--tts", "Test TTS: type text, hear it spoken"),
    ("--stt", "Test STT: speak, see transcript printed"),
    ("--detect", "Test detection: live webcam with YOLO boxes side-by-side"),
    ("--gui", "Visualize the capture and detections side-by-side"),
    ("--voices", "Listen to pyttsx3 voices"),
    ("--camera", "View camera and regions in console")
]

# Seconds before an unchanged guidance instruction is spoken again, so the
# user hears reassurance without a wall of speech.
GUIDANCE_INTERVAL_SECONDS = 8.0

# Directory captured photos are saved to.
CAPTURES_DIR = Path("captures")

# Collection of TTS phrases


class Phrases(StrEnum):
    LIST_OBJECTS = "The detected objects were "
    PROMPT_CHOOSE_OBJECT = "Which object would you like to frame?"
    INVALID_RESPONSE = "Invalid response. Try again."
    PROMPT_CHOOSE_REGION = "Choose a region in which to frame the "
    REPORT_OBJECT_AREA = "The object currently fills "
    NO_OBJECTS = "I could not detect any objects. Please try again."
    OBJECT_LOST = "I cannot see the "
    HOLD_STILL = "Hold still."
    SAVED = "Picture saved."


def get_args() -> Namespace:
    """Populate argument parser namespace."""
    parser = argparse.ArgumentParser(
        description="CS 4900 Camera App for Visually Impaired")
    group = parser.add_mutually_exclusive_group()
    for arg, help_text in ARGS:
        group.add_argument(arg,
                           action="store_true",
                           help=help_text)
    parser.add_argument("--voice",
                        type=int,
                        default=1,
                        help="pyttsx3 voice index for TTS output (see --voices)")
    parser.add_argument("--rate",
                        type=int,
                        default=150,
                        help="pyttsx3 voice speaking rate")
    return parser.parse_args()


def guide_to_capture(camera: Camera,
                     detector: Detector,
                     sio: SpeechIO,
                     target_label: str,
                     region_name: str,
                     frame: MatLike,
                     detections: list[Detection]) -> MatLike | None:
    """Speak movement instructions until `target_label` sits inside `region_name`.

    Runs detection on a fresh frame each iteration rather than capturing,
    waiting, and recapturing, so a correction is spoken the moment the camera
    drifts. `frame`/`detections` are the first frame and its detections,
    already captured by the caller. Returns the frame the object was framed
    in, or None if the user quit the preview window (pressed q or Esc).
    """
    frame_region = camera.regions[region_name]
    last_said: str | None = None
    last_time = 0.0

    while True:
        match = next((d for d in detections if d[0] == target_label), None)
        if match is None:
            instruction = Phrases.OBJECT_LOST + target_label
        else:
            instruction = geometry.guidance(match[1], frame_region, *camera.resolution)

        annotated = overlays.overlay_regions(frame.copy(), camera.regions, region_name)
        if match is not None:
            cv2.rectangle(annotated, match[1][:2], match[1][2:], (0, 0, 255), 2)
        cv2.putText(annotated, instruction or "Hold still", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.imshow("Detections", annotated)

        if instruction is None:
            return frame

        # Speak only when the advice changes, or periodically to reassure.
        now = time.monotonic()
        if (instruction != last_said) or (now - last_time) >= GUIDANCE_INTERVAL_SECONDS:
            sio.speak(instruction)
            last_said, last_time = instruction, now

        if cv2.waitKey(1) & 0xFF in (ord("q"), 27):  # 27 = Esc
            return None

        frame = camera.read_frame()
        _, detections = detector.detect(frame)


def main() -> None:

    # Debug
    # -------------------------------------------------------------------------

    # Debug modes: each runs in isolation and skips the main pipeline.
    args: Namespace = get_args()

    if args.detect:
        debug.debug_detect(Detector())
        return

    if args.camera:
        camera: Camera = Camera()
        debug.debug_camera(camera)
        return

    if args.tts or args.stt or args.voices:
        sio: SpeechIO = SpeechIO(voice_index=args.voice,
                                 rate=args.rate)
        if args.tts:
            debug.debug_tts(sio)
        elif args.stt:
            debug.debug_stt(sio)
        elif args.voices:
            sio.list_voices()
        return

    # Main pipeline
    # -------------------------------------------------------------------------

    camera: Camera = Camera()
    detector: Detector = Detector()
    sio: SpeechIO = SpeechIO(voice_index=args.voice,
                             rate=args.rate)

    # 1. Capture image
    capture = camera.capture_image()

    # 2. Detect objects
    result, detections = detector.detect(capture)
    # if args.gui:
    cv2.imshow("Detections", overlays.overlay_regions(
        result.plot(), camera.regions))
    cv2.waitKey(1)

    # 3. List detected objects, deduplicated but kept in detection order
    objects = list(dict.fromkeys(label for label, _, _ in detections))
    if not objects:
        sio.speak(Phrases.NO_OBJECTS)
        return
    sio.speak(Phrases.LIST_OBJECTS + ", ".join(objects))

    # 4. Ask object choice
    sio.speak(Phrases.PROMPT_CHOOSE_OBJECT)

    # 5. Get user object choice
    target_label = sio.make_choice(choices=objects,
                                   invalid_response=Phrases.INVALID_RESPONSE)

    # 6. Ask object framing
    sio.speak(Phrases.PROMPT_CHOOSE_REGION +
              target_label + ": " + ", ".join(camera.region_names))

    # 7. Get user framing region choice
    region_name = sio.make_choice(choices=camera.region_names,
                                  invalid_response=Phrases.INVALID_RESPONSE)
    sio.speak(f"You chose: {region_name}")

    # 8. Calculate object area % in frame
    frame_region = camera.regions[region_name]
    detection_region = next((d[1] for d in detections if d[0] == target_label), None)
    if detection_region is not None:
        area_percent = geometry.overlap_ratio(detection_region, frame_region) * 100
        sio.speak(f"{Phrases.REPORT_OBJECT_AREA}{area_percent:.0f}"
                  f" percent of the {region_name} region.")

    # 9-15. Guide the user until the object sits in the chosen region, then
    # capture. Steps 9 through 15 all live inside this loop: it measures
    # coverage, speaks a direction, and re-detects on the next frame.
    framed = guide_to_capture(camera, detector, sio, target_label,
                              region_name, capture, detections)
    if framed is None:  # User quit the preview window
        return

    sio.speak(Phrases.HOLD_STILL)
    CAPTURES_DIR.mkdir(exist_ok=True)
    filename = CAPTURES_DIR / f"capture_{datetime.now():%Y%m%d_%H%M%S}.jpg"
    cv2.imwrite(str(filename), framed)
    sio.speak(Phrases.SAVED)
    print(f"Saved {filename}")


if __name__ == "__main__":
    main()
