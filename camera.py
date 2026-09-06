import cv2

CAMERA_INDEX = 0

def capture_initial_image(show_gui: bool):
    """Open the webcam, grab one still frame, and return it (BGR ndarray).

    The frame is captured as soon as the camera is ready. When show_gui is True,
    a window shows the live feed (left) next to the frozen capture (right); press
    any key (or close the window) to continue.
    """
    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        raise RuntimeError(f"Error: could not open camera at index {CAMERA_INDEX}!")

    try:
        # Discard a few frames so exposure and white balance can settle
        for _ in range(5):
            cap.read()

        ok, captured = cap.read()
        if not ok or captured is None:
            raise RuntimeError("Error: failed to read a frame from the camera!")

        if show_gui:
            window_name = "Live View (left) - Capture View (right) [Press any key to exit]"
            while True:
                ok, live = cap.read()
                if not ok or live is None:
                    break
                cv2.imshow(window_name, cv2.hconcat([live, captured]))
                if cv2.waitKey(30) != -1:
                    break
                if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
                    break
            cv2.destroyWindow(window_name)

        return captured
    finally:
        cap.release()
        cv2.destroyAllWindows()