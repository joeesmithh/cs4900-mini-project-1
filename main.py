import argparse
import debug
import cv2
import overlays
import geometry
from detector import Detector
from speech_io import SpeechIO
from argparse import Namespace  # Type hinting for argparse arguments
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

# Collection of TTS phrases


class Phrases(StrEnum):
    LIST_OBJECTS = "The detected objects were "
    PROMPT_CHOOSE_OBJECT = "Which object would you like to frame?"
    INVALID_RESPONSE = "Invalid response. Try again."
    PROMPT_CHOOSE_REGION = "Choose a region in which to frame the "
    REPORT_OBJECT_AREA = "The object currently fills "


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

    # 3. List detected objects
    objects = [label for label, _, _ in detections]
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
    detection_region = next((d[1] for d in detections if d[0] == target_label))
    area_percent = geometry.overlap_ratio(detection_region, frame_region) * 100
    sio.speak(f"{Phrases.REPORT_OBJECT_AREA}{area_percent:.0f}"
              f" percent of the {region_name} region.")

    # Show chosen frame and chosen regions, with object area in region shaded
    # if args.gui:
    overlays.show_detection_overlay(capture, camera.regions, region_name,
                                    detection_region, target_label)

    # TODO: 9. Calculate camera movement direction
    # TODO: 10. Instruct user where to move camera
    # TODO: 11. Wait for camera movement
    # TODO: 12. Wait for camera stationary
    # TODO: 13. Capture Image
    # TODO: 14. Detect objects
    # TODO: 15. Is object still in scene?


if __name__ == "__main__":
    main()
