import cv2
import numpy as np
from camera import CAMERA_INDEX
from detector import Detector
from speech_io import SpeechIO
from camera import Camera


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
            sio.listen()
    except KeyboardInterrupt:
        print("\nExiting STT debug.")


def debug_detect(detector: Detector) -> None:
    """Live webcam loop: showsYOLO's annotated frame, refreshed as
    fast as the CPU can run it. Press 'q' or Esc in the window to quit.
    """
    # Open the camera once and hold it for the whole loop (unlike
    # camera.capture_image(), which reopens it every call).
    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        raise RuntimeError(
            f"Error: could not open camera at index {CAMERA_INDEX}!")

    print("Detection debug (press 'q' or Esc in the window to quit).")
    try:
        while True:
            ok, frame = cap.read()
            if not ok or frame is None:
                break

            result = detector.detect(frame)
            annotated = result.plot()  # BGR frame with boxes + labels drawn

            cv2.imshow("Detections  (press q to quit)", annotated)

            if cv2.waitKey(1) & 0xFF in (ord("q"), 27):  # 27 = Esc
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()

def debug_camera(camera: Camera):
    print(f"Camera resolution: {camera.resolution}")
    print(f"Region names: {camera.region_names}")
    print(f"Regions: {camera.regions}")
    cv2.imshow("Region view", camera.capture_with_regions())
    cv2.waitKey(0)
    cv2.destroyAllWindows()