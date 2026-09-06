import argparse
import camera
import debug

# Tuple: ("<flag>", "<help message>")
ARGS = [
    ("--tts", "Test TTS: type text, hear it spoken"),
    ("--stt", "Test STT: speak, see transcript printed"),
    ("--gui", "Show the live webcam feed and the captured frame side-by-side")
]


def get_args() -> argparse.Namespace:
    """Populate argument parser namespace.s"""
    parser = argparse.ArgumentParser(
        description="CS 4900 Camera App for Visually Impaired")
    group = parser.add_mutually_exclusive_group()
    for arg, help in ARGS:
        group.add_argument(arg, action="store_true",
                           help=help)
    return parser.parse_args()


def main() -> None:

    # Debug
    # -------------------------------------------------------------------------
    args = get_args()

    # Debug modes: each runs in isolation and skips the main pipeline.
    if args.tts or args.stt:
        from speech_io import SpeechIO
        sio = SpeechIO()
        if args.tts:
            debug.debug_tts(sio)
        elif args.stt:
            debug.debug_stt(sio)
        return

    # Main pipeline
    # -------------------------------------------------------------------------

    # Capture image
    try:
        captured_frame = camera.capture_initial_image(show_gui=args.gui)
    except RuntimeError as e:
        print(f"Error: camera error: {e}!")
        return

    h, w = captured_frame.shape[:2]
    print(f"Captured initial frame: {w}x{h}")

    # TODO: Detect objects
    # TODO: List detected objects
    # TODO: Ask user which object to frame
    # TODO: Wait for user response
    # TODO: Ask object framing
    # TODO: Wait for user response
    # TODO: Calculate object area % in frame
    # TODO: Calculate camera movement direction
    # TODO: Instruct user where to move camera
    # TODO: Wait for camera movement
    # TODO: Wait for camera stationary
    # TODO: Capture Image
    # TODO: Detect objects
    # TODO: Is object still in scene?


if __name__ == "__main__":
    main()
