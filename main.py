import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description="CS 4900 Camera App for Visually Impaired")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--debug-tts", action="store_true", help="Test TTS: type text, hear it spoken")
    group.add_argument("--debug-stt", action="store_true", help="Test STT: speak, see transcript printed")
    args = parser.parse_args()

    if args.debug_tts or args.debug_stt:
        from speech_io import SpeechIO
        sio = SpeechIO()
        if args.debug_tts:
            from debug import debug_tts
            debug_tts(sio)
        else:
            from debug import debug_stt
            debug_stt(sio)
    else:
        print("Full app not yet implemented. Run with --debug-tts or --debug-stt to test speech I/O.")


if __name__ == "__main__":
    main()
