import cv2
from cv2.typing import MatLike  # Type hinting for cv2 images and matrices

CAMERA_INDEX = 0

# Frames discarded on a fresh capture so exposure and white balance can settle.
WARMUP_FRAMES = 5


def open_camera(index: int = CAMERA_INDEX) -> cv2.VideoCapture:
    """Open the webcam and return the live handle.

    The caller owns the handle and must release() it. Callers that need many
    frames should hold one handle rather than reopening per frame, since only
    one process at a time can stream from the device.
    """
    cap = cv2.VideoCapture(index)
    if not cap.isOpened():
        raise RuntimeError(
            f"Error: could not open camera at index {index}!")
    return cap


def read_frame(cap: cv2.VideoCapture, warmup: int = 0) -> MatLike:
    """Grab one frame from an already-open camera (BGR ndarray)."""
    for _ in range(warmup):
        cap.read()

    ok, captured = cap.read()
    if not ok or captured is None:
        raise RuntimeError(
            "Failed to read a frame from the camera")
    return captured


def capture_image() -> MatLike:
    """Open the webcam, grab one still frame, and return it (BGR ndarray).
    The frame is captured as soon as the camera is ready.
    """
    cap = open_camera()
    try:
        return read_frame(cap, warmup=WARMUP_FRAMES)
    finally:
        cap.release()
