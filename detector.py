from cv2.typing import MatLike  # Type hinting for cv2 images and matrices
from ultralytics import YOLO
from ultralytics.engine.results import Results  # Type hint for a single result

# YOLOv8 nano weights. Ultralytics downloads this file on first use and then
# loads it from the local cache; *.pt is gitignored.
MODEL_NAME = "yolo26n.pt"

# One detection: class label, pixel bounding box (x1, y1, x2, y2), confidence.
Detection = tuple[str, tuple[int, int, int, int], float]


class Detector:
    """YOLOv8 wrapper. Loads the model once, then reuses it for every frame."""

    def __init__(self, model_name: str = MODEL_NAME) -> "Detector":
        self._model = YOLO(model_name)

    def detect(self, frame: MatLike) -> Results:
        """Run detection on one BGR frame and return the raw ultralytics result.

        The result carries the boxes and can draw itself with result.plot().
        verbose=False silences per-frame console output so it doesn't flood
        a real-time loop.
        """
        results = self._model.predict(frame, verbose=False)
        return results[0]


def parse_detections(result: Results) -> list[Detection]:
    """Flatten an ultralytics result into (label, bbox, conf) tuples."""
    detections: list[Detection] = []
    for box in result.boxes:
        label = result.names[int(box.cls[0])]  # names maps class id -> string
        x1, y1, x2, y2 = (int(coord) for coord in box.xyxy[0])
        confidence = float(box.conf[0])
        detections.append((label, (x1, y1, x2, y2), confidence))
    return detections
