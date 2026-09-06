import argparse
from debug import (
    debug_tts,
    debug_stt
)

# Tuple: ("<flag>", "<help message>")
DEBUG_ARGS = [
    ("--tts", "Test TTS: type text, hear it spoken"),
    ("--stt", "Test STT: speak, see transcript printed")
]


def get_args() -> argparse.Namespace:
    """Populate argument parser namespace.s"""
    parser = argparse.ArgumentParser(
        description="CS 4900 Camera App for Visually Impaired")
    group = parser.add_mutually_exclusive_group()
    for arg, help in DEBUG_ARGS:
        group.add_argument(arg, action="store_true",
                           help=help)
    return parser.parse_args()


def main() -> None:

    # Debug
    # -------------------------------------------------------------------------
    args = get_args()
    debug_arg_states = [b for _, b in args._get_kwargs()]
    if any(debug_arg_states):
        from speech_io import SpeechIO
        sio = SpeechIO()
        if args.debug_tts:
            debug_tts(sio)
        else:
            debug_stt(sio)
        return

    # Main pipeline
    # -------------------------------------------------------------------------
    print("Full app not yet implemented. Run with --debug-tts or"
          "--debug-stt to test speech I/O.")


if __name__ == "__main__":
    main()
