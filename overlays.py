import cv2
from cv2.typing import MatLike  # Type hinting for cv2 images and matrices
from framing import Region, intersection


def overlay_regions(frame: MatLike,
                    regions: dict[str, Region],
                    region: str | None = None) -> MatLike:
    """Overlay region rectangles on top of an image.

    If `region` is given, only that named region is drawn; otherwise
    every region in `regions` is drawn.
    """
    box_color = (0, 255, 0)       # BGR: green for the four quadrants
    center_color = (0, 255, 255)  # BGR: yellow for the overlapping center box

    if region is not None:
        if region not in regions:
            raise ValueError(f"Unknown region: {region!r}")
        regions = {region: regions[region]}

    for name, xyxy in regions.items():
        color = center_color if name == "center" else box_color
        cv2.rectangle(frame, xyxy[:2], xyxy[2:], color, 2)
        label_org = (xyxy[0] + 5, xyxy[1] + 15)
        cv2.putText(frame, name, label_org,
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2, cv2.LINE_AA)
    return frame


def show_detection_overlay(frame: MatLike,
                           regions: dict[str, Region],
                           region_name: str,
                           detection_region: Region,
                           label: str) -> None:
    """Display frame with region grid, shaded overlap, and object bbox.

    Blocks until a key is pressed, then closes the window.
    """
    overlay = overlay_regions(frame, regions, region_name)
    color = (0, 0, 255)

    frame_region = regions[region_name]
    overlap_rect = intersection(detection_region, frame_region)
    if overlap_rect is not None:
        shaded = overlay.copy()
        cv2.rectangle(shaded, overlap_rect[:2], overlap_rect[2:], color, cv2.FILLED)
        # Blend rather than draw directly so the region grid and image stay visible.
        cv2.addWeighted(shaded, 0.4, overlay, 0.6, 0, dst=overlay)

    cv2.rectangle(overlay, detection_region[:2], detection_region[2:], color, 2)
    cv2.putText(overlay, label, (detection_region[0], detection_region[1] - 5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2, cv2.LINE_AA)
    cv2.imshow("Detections", overlay)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
