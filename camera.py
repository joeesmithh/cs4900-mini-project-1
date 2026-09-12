import cv2
from cv2.typing import MatLike  # Type hinting for cv2 images and matrices
from geometry import Region

CAMERA_INDEX = 0

class Camera:
    """Wraps a webcam device: exposes its resolution and named regions."""

    def __init__(self,
                 camera_index: int = CAMERA_INDEX):
        """Open the camera at `camera_index` and compute its regions."""
        self._capture = cv2.VideoCapture(camera_index)
        if not self._capture.isOpened():
            raise RuntimeError(f"Error: could not open camera at index {camera_index}!")
        self._height, self._width = self._get_image(self._capture).shape[:2]
        self._regions = self._get_regions(self._width, self._height)

    def __del__(self):
        """Close capture on object deletion."""
        self._capture.release()

    @property
    def resolution(self) -> tuple[int, int]:
        """Return the (width, height) of frames captured by this camera."""
        return (self._width, self._height)

    @property
    def regions(self) -> dict[str, Region]:
        """Return each named region's pixel bounding box."""
        return self._regions

    @property
    def region_names(self) -> list[str]:
        """Return the names of the available regions."""
        return list(self._regions)

    def _get_regions(self, width: int, height: int) -> dict[str, Region]:
        frame_width      = width // 2
        frame_height     = height // 2
        return {
            "top left": (0, 0, frame_width, frame_height),
            "top right": (frame_width, 0, width, frame_height),
            "bottom left": (0, frame_height, frame_width, height),
            "bottom right": (frame_width, frame_height, width, height),
            "center": (frame_width // 2, frame_height // 2,
                       frame_width // 2 + frame_width,
                       frame_height // 2 + frame_height)
        }

    def _get_image(self, capture: cv2.VideoCapture) -> MatLike:
        """Capture and validate an image"""
        ok, captured = capture.read()
        if not ok or captured is None:
            raise RuntimeError("Failed to read a frame from the camera")
        return captured

    def capture_image(self) -> MatLike:
        """Take a webcam photo."""
        # Discard a few frames so exposure and white balance can settle
        for _ in range(5):
            self._capture.read()

        # Capture image
        return self._get_image(self._capture)
