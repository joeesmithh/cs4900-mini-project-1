import cv2
from cv2.typing import MatLike  # Type hinting for cv2 images and matrices

CAMERA_INDEX = 0

class Camera:
    def __init__(self,
                 camera_index: int = CAMERA_INDEX):
        self._capture = cv2.VideoCapture(camera_index)
        if not self._capture.isOpened():
            raise RuntimeError(f"Error: could not open "
                               "camera at index {CAMERA_INDEX}!")
        self._height, self._width = self._get_image(self._capture).shape[:2]
        self._regions = self._get_regions(self._width, self._height)

    def __del__(self):
        """Close capture on object deletion."""
        self._capture.release()
        
    @property
    def resolution(self) -> tuple[int, int]:
        return (self._width, self._height)
    
    @property
    def regions(self) -> dict[str, list[tuple[int, int]]]:
        return self._regions
    
    @property
    def region_names(self) -> list[str]:
        return [region for region in self._regions]

    def _get_regions(self, width: int, height: int) -> dict[str, list[tuple[int, int]]]:
        frame_width      = width // 2
        frame_height     = height // 2
        top_left         = (0, 0)
        top_middle       = (frame_width, 0)
        middle_left      = (0, frame_height)
        middle_middle    = (frame_width, frame_height)
        middle_right     = (width, frame_height)
        bottom_middle    = (frame_width, height)
        bottom_right     = (width, height)
        return {
            "top left": [top_left, middle_middle],
            "top right": [top_middle, middle_right],
            "bottom left": [middle_left, bottom_middle],
            "bottom right": [middle_middle, bottom_right],
            "center": [(frame_width // 2,
                        frame_height // 2),
                       (frame_width // 2 + frame_width,
                        frame_height // 2 + frame_height)]
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

    def capture_with_regions(self) -> MatLike:
        """Take a photo and return it with every named region drawn on top.
        Each region rectangle is labelled with its name; the overlapping.
        """
        frame = self.capture_image().copy()
        box_color = (0, 255, 0)       # BGR: green for the four quadrants
        center_color = (0, 255, 255)  # BGR: yellow for the overlapping center box
        for name, (top_left, bottom_right) in self._regions.items():
            color = center_color if name == "center" else box_color
            cv2.rectangle(frame, top_left, bottom_right, color, 2)
            label_org = (top_left[0] + 5, top_left[1] + 22)
            cv2.putText(frame, name, label_org,
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2, cv2.LINE_AA)
        return frame