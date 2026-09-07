import cv2
from cv2.typing import MatLike  # Type hinting for cv2 images and matrices

CAMERA_INDEX = 0


def capture_image() -> MatLike:
    """Open the webcam, grab one still frame, and return it (BGR ndarray).
    The frame is captured as soon as the camera is ready.
    """
    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        raise RuntimeError(
            f"Error: could not open camera at index {CAMERA_INDEX}!")

    try:
        # Discard a few frames so exposure and white balance can settle
        for _ in range(5):
            cap.read()

        # Capture image
        ok, captured = cap.read()
        if not ok or captured is None:
            raise RuntimeError(
                "Failed to read a frame from the camera")

        return captured
    finally:
        cap.release()
