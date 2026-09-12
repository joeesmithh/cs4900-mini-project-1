Region = tuple[int, int, int, int]

# Fraction of the object's area that must sit inside the target region
# before the photograph is taken.
CAPTURE_THRESHOLD = 0.85

# Overhang smaller than this fraction of the frame is ignored, so guidance
# stops nudging once the object is close enough instead of oscillating on
# camera jitter.
DEADZONE = 0.03


def intersection(bbox: Region, region: Region) -> Region | None:
    """Return the overlapping rectangle between bbox and region.

    bbox and region are both (x1, y1, x2, y2) pixel coordinates. Returns
    None if the two rectangles do not overlap.
    """
    ix1 = max(bbox[0], region[0])
    iy1 = max(bbox[1], region[1])
    ix2 = min(bbox[2], region[2])
    iy2 = min(bbox[3], region[3])
    if ix2 <= ix1 or iy2 <= iy1:
        return None
    return (ix1, iy1, ix2, iy2)


def overlap_ratio(bbox: Region, region: Region) -> float:
    """Return the fraction of bbox's area that falls inside region.

    bbox and region are both (x1, y1, x2, y2) pixel coordinates. Returns
    0.0 if the two rectangles do not overlap.
    """
    overlap_rect = intersection(bbox, region)
    if overlap_rect is None:
        return 0.0
    ix1, iy1, ix2, iy2 = overlap_rect
    intersection_area = (ix2 - ix1) * (iy2 - iy1)
    bbox_area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
    return intersection_area / bbox_area


def guidance(bbox: Region, region: Region,
            frame_width: int, frame_height: int) -> str | None:
    """Spoken instruction that moves bbox toward region, or None once framed.

    bbox and region are (x1, y1, x2, y2) pixel coordinates; frame_width and
    frame_height are the full frame size, so the deadzone scales with
    resolution. Returns None once overlap_ratio(bbox, region) reaches
    CAPTURE_THRESHOLD -- the caller should then say "Hold still" and capture.
    """
    if overlap_ratio(bbox, region) >= CAPTURE_THRESHOLD:
        return None

    bx1, by1, bx2, by2 = bbox
    rx1, ry1, rx2, ry2 = region

    # The object is bigger than the region: no amount of aiming fits it, and
    # without this check the caller would be nudged back and forth forever.
    if (bx2 - bx1) > (rx2 - rx1) or (by2 - by1) > (ry2 - ry1):
        return "Move camera further away from object"

    # Pixels the box pokes outside region on each axis. Positive dx means the
    # box overhangs on the left and must move right; positive dy means it
    # overhangs on top and must move down. Measuring overhang rather than the
    # distance between centers means both terms reach zero exactly when the
    # box is fully inside the region.
    dx = max(0, rx1 - bx1) - max(0, bx2 - rx2)
    dy = max(0, ry1 - by1) - max(0, by2 - ry2)

    horizontal = abs(dx) / frame_width >= DEADZONE
    vertical = abs(dy) / frame_height >= DEADZONE

    if not horizontal and not vertical:
        return None

    vertical_word = "up" if dy > 0 else "down"
    horizontal_word = "left" if dx > 0 else "right"

    if horizontal and vertical:
        return f"Move {vertical_word} and to the {horizontal_word}"
    if vertical:
        return f"Move {vertical_word}"
    return f"Move {horizontal_word}"
