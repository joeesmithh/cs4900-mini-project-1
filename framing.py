Region = tuple[int, int, int, int]

# Fraction of the object's area that must sit inside the target region
# before the photograph is taken. Used by the "bbox" framing method.
CAPTURE_THRESHOLD = 0.95

# Overhang smaller than this fraction of the frame is ignored, so guidance
# stops nudging once the object is close enough instead of oscillating on
# camera jitter. Used by the "bbox" framing method.
DEADZONE = 0.03

# How far the bbox's center may sit from the region's center before capture
# triggers, as a fraction of the region's own width/height. Used by the
# "distance" framing method.
CENTER_DEADZONE = 0.1


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


def guidance(bbox: Region, region: Region, frame_width: int, frame_height: int,
            method: str = "bbox") -> str | None:
    """Spoken instruction that moves bbox toward region, or None once framed.

    bbox and region are (x1, y1, x2, y2) pixel coordinates; frame_width and
    frame_height are the full frame size. method picks how "framed" is
    judged:
      - "bbox": framed once overlap_ratio(bbox, region) reaches
        CAPTURE_THRESHOLD. Only checks containment, so a small object can
        pass while sitting in a corner of a large region.
      - "distance": framed once the bbox's center sits within
        CENTER_DEADZONE of the region's center, scaled to the region's own
        size, so the object must actually be centered in the region.

    Returns None once framed -- the caller should then say "Hold still" and
    capture.
    """
    if method == "bbox":
        return _guidance_by_bbox(bbox, region, frame_width, frame_height)
    if method == "distance":
        return _guidance_by_distance(bbox, region)
    raise ValueError(f"Unknown framing method: {method!r}")


def _guidance_by_bbox(bbox: Region, region: Region,
                      frame_width: int, frame_height: int) -> str | None:
    """Containment-based guidance: framed once overlap_ratio(bbox, region)
    reaches CAPTURE_THRESHOLD, direction chosen from how far bbox pokes
    outside region on each axis."""
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

    do_horizontal_move = abs(dx) / frame_width >= DEADZONE
    do_vertical_move = abs(dy) / frame_height >= DEADZONE

    return _direction_phrase(dx, dy, do_horizontal_move, do_vertical_move)


def _guidance_by_distance(bbox: Region, region: Region) -> str | None:
    """Center-based guidance: framed once the bbox's center sits within
    CENTER_DEADZONE of the region's center (relative to region size), so a
    small object must reach the middle of the region rather than merely
    fit somewhere inside it."""
    bx1, by1, bx2, by2 = bbox
    rx1, ry1, rx2, ry2 = region

    # The object is bigger than the region: no amount of aiming fits it, and
    # without this check the caller would be nudged back and forth forever.
    if (bx2 - bx1) > (rx2 - rx1) or (by2 - by1) > (ry2 - ry1):
        return "Move camera further away from object"

    region_width = rx2 - rx1
    region_height = ry2 - ry1

    # Positive dx means the region's center lies to the right of the box's
    # center, so the box must move right; positive dy means the box must
    # move down. Deadzone is a fraction of the region's own size rather than
    # the frame's, so the tolerance shrinks for small target regions.
    dx = (rx1 + rx2) / 2 - (bx1 + bx2) / 2
    dy = (ry1 + ry2) / 2 - (by1 + by2) / 2

    do_horizontal_move = abs(dx) / region_width >= CENTER_DEADZONE
    do_vertical_move = abs(dy) / region_height >= CENTER_DEADZONE

    return _direction_phrase(dx, dy, do_horizontal_move, do_vertical_move)


def _direction_phrase(dx: float, dy: float, do_horizontal_move: bool, do_vertical_move: bool) -> str | None:
    """Turn signed axis offsets into a spoken direction, or None if both
    axes are already within their deadzone. Positive dx/dy mean the box
    needs to shift right/down within the frame; the spoken instruction is
    given in camera-movement terms, which is why the words are inverted.
    """
    if not do_horizontal_move and not do_vertical_move:
        return None

    vertical_word = "up" if dy > 0 else "down"
    horizontal_word = "left" if dx > 0 else "right"

    if do_horizontal_move and do_vertical_move:
        return f"Move {vertical_word} and to the {horizontal_word}"
    if do_vertical_move:
        return f"Move {vertical_word}"
    return f"Move {horizontal_word}"
