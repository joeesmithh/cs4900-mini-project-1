import threading
import cv2
from camera import WARMUP_FRAMES
from cv2.typing import MatLike  # Type hinting for cv2 images and matrices
from dataclasses import dataclass, field
from framing import Bbox

# Overlay colors in BGR.
REGION_COLOR = (0, 255, 255)  # Yellow: the region the user asked for
BOX_COLOR = (0, 255, 0)       # Green: detected objects
TEXT_COLOR = (255, 255, 255)
WINDOW = "Camera  (press q to quit)"

# Consecutive failed camera reads tolerated before the feed is declared dead.
MAX_READ_FAILURES = 30

# Seconds to wait for the first frame before giving up on the camera.
FIRST_FRAME_TIMEOUT = 10.0


@dataclass
class Overlay:
    """What to draw on top of the live video."""
    boxes: list[tuple[Bbox, str]] = field(default_factory=list)  # (box, label)
    region: Bbox | None = None
    text: str | None = None


class Preview(threading.Thread):
    """Own the camera on a background thread and optionally show live video.

    The main thread blocks for seconds at a time on speech and detection,
    which would freeze any window it drew itself. Reading frames here keeps
    the video moving, and latest() always returns the newest frame, so there
    are no stale buffered frames to flush after speaking.

    Only this thread touches the capture handle or the window: OpenCV's GUI
    must be created and pumped from a single thread.
    """

    def __init__(self, cap: cv2.VideoCapture, show: bool) -> None:
        super().__init__(daemon=True)
        self._cap = cap
        self._show = show
        self._frame: MatLike | None = None
        self._overlay = Overlay()
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._ready = threading.Event()          # First usable frame arrived
        self.quit_requested = threading.Event()  # User pressed q or Esc
        self.failed = threading.Event()          # Camera stopped delivering

    def run(self) -> None:
        failures = 0
        # Discard the first frames so exposure and white balance can settle.
        for _ in range(WARMUP_FRAMES):
            self._cap.read()
        try:
            while not self._stop_event.is_set():
                ok, frame = self._cap.read()
                if not ok or frame is None:
                    failures += 1
                    if failures > MAX_READ_FAILURES:
                        self.failed.set()
                        self._ready.set()  # Wake any waiter so it sees failed
                        return
                    continue
                failures = 0

                with self._lock:
                    self._frame = frame
                    overlay = self._overlay
                self._ready.set()

                if self._show:
                    cv2.imshow(WINDOW, self._draw(frame, overlay))
                    if cv2.waitKey(1) & 0xFF in (ord("q"), 27):  # 27 = Esc
                        self.quit_requested.set()
        finally:
            if self._show:
                cv2.destroyAllWindows()

    def latest(self) -> MatLike:
        """Newest frame from the camera (BGR ndarray)."""
        if not self._ready.wait(FIRST_FRAME_TIMEOUT) or self.failed.is_set():
            raise RuntimeError("Camera stopped delivering frames")
        with self._lock:
            return self._frame

    def set_overlay(self, overlay: Overlay) -> None:
        """Replace what is drawn over the video from the next frame on."""
        with self._lock:
            self._overlay = overlay

    def stop(self) -> None:
        """Stop reading and close the window; blocks until the thread exits."""
        self._stop_event.set()
        self.join()

    @staticmethod
    def _draw(frame: MatLike, overlay: Overlay) -> MatLike:
        annotated = frame.copy()

        if overlay.region is not None:
            rx1, ry1, rx2, ry2 = overlay.region
            cv2.rectangle(annotated, (rx1, ry1), (rx2, ry2), REGION_COLOR, 2)

        for (bx1, by1, bx2, by2), label in overlay.boxes:
            cv2.rectangle(annotated, (bx1, by1), (bx2, by2), BOX_COLOR, 2)
            cv2.putText(annotated, label, (bx1, max(by1 - 6, 14)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, BOX_COLOR, 2)

        if overlay.text:
            cv2.putText(annotated, overlay.text, (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, TEXT_COLOR, 2)
        return annotated
