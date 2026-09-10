import cv2
import numpy as np
from camera import open_camera
from cv2.typing import MatLike  # Type hinting for cv2 images and matrices
from framing import Bbox
from detector import Detector
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
            sio.listen()
    except KeyboardInterrupt:
        print("\nExiting STT debug.")


def debug_detect(detector: Detector) -> None:
    """Live webcam loop: showsYOLO's annotated frame, refreshed as
    fast as the CPU can run it. Press 'q' or Esc in the window to quit.
    """
    # Open the camera once and hold it for the whole loop (unlike
    # camera.capture_image(), which reopens it every call).
    cap = open_camera()

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


# Overlay colors in BGR, plus the window the framing loop draws into.
REGION_COLOR = (0, 255, 255)  # Yellow: the region the user asked for
BOX_COLOR = (0, 255, 0)       # Green: the object being tracked
TEXT_COLOR = (255, 255, 255)
FRAMING_WINDOW = "Framing  (press q to quit)"


def show_framing(frame: MatLike,
                 region: Bbox,
                 box: Bbox | None,
                 instruction: str | None) -> None:
    """Draw the target region, the tracked object, and the spoken instruction.

    Used by --gui so a sighted developer can watch the guidance loop; the app
    itself never needs a window.
    """
    annotated = frame.copy()

    rx1, ry1, rx2, ry2 = region
    cv2.rectangle(annotated, (rx1, ry1), (rx2, ry2), REGION_COLOR, 2)

    if box is not None:
        bx1, by1, bx2, by2 = box
        cv2.rectangle(annotated, (bx1, by1), (bx2, by2), BOX_COLOR, 2)

    cv2.putText(annotated, instruction or "Framed", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, TEXT_COLOR, 2)
    cv2.imshow(FRAMING_WINDOW, annotated)
