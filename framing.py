# Fraction of the object's area that must sit inside the target region before
# the photograph is taken.
COVERAGE_TARGET = 0.90

# Overhang smaller than this fraction of the frame is ignored, so the app stops
# nudging once the object is close enough instead of oscillating on jitter.
DEADZONE = 0.03

# Size of the center region as a fraction of the frame.
CENTER_SCALE = 1 / 3

# Pixel box (x1, y1, x2, y2), the same convention ultralytics uses.
Bbox = tuple[int, int, int, int]


def region_bbox(region: str, width: int, height: int) -> Bbox:
    """Pixel box of a named region within a width x height frame.

    The four quadrants tile the frame; the center is a smaller box straddling
    all four, so "center" is a distinct target rather than a corner.
    """
    mid_x, mid_y = width // 2, height // 2
    match region:
        case "top left":
            return (0, 0, mid_x, mid_y)
        case "top right":
            return (mid_x, 0, width, mid_y)
        case "bottom left":
            return (0, mid_y, mid_x, height)
        case "bottom right":
            return (mid_x, mid_y, width, height)
        case "center":
            half_w = int(width * CENTER_SCALE / 2)
            half_h = int(height * CENTER_SCALE / 2)
            return (mid_x - half_w, mid_y - half_h,
                    mid_x + half_w, mid_y + half_h)
    raise ValueError(f"Unknown region: {region}")


def coverage(box: Bbox, region: Bbox) -> float:
    """Fraction of the object's area that lies inside the region.

    This is intersection over the *object's* area, not IoU: the assignment
    asks what percentage of the object sits in the chosen location, so the
    region's size must not dilute the score.
    """
    bx1, by1, bx2, by2 = box
    rx1, ry1, rx2, ry2 = region
    overlap_w = max(0, min(bx2, rx2) - max(bx1, rx1))
    overlap_h = max(0, min(by2, ry2) - max(by1, ry1))
    area = (bx2 - bx1) * (by2 - by1)
    return (overlap_w * overlap_h) / area if area else 0.0


def guidance(box: Bbox, region: Bbox, width: int, height: int) -> str | None:
    """Spoken instruction that moves the object toward the region.

    Returns None once the object is framed well enough to photograph.
    """
    if coverage(box, region) >= COVERAGE_TARGET:
        return None

    bx1, by1, bx2, by2 = box
    rx1, ry1, rx2, ry2 = region

    # The object is bigger than the region, so no amount of aiming will fit it
    # and the caller would otherwise be nudged back and forth forever.
    if (bx2 - bx1) > (rx2 - rx1) or (by2 - by1) > (ry2 - ry1):
        return "Move farther away from the object"

    # Pixels the object must travel to sit fully inside the region. Positive
    # means right/down. Measuring the overhang rather than the distance between
    # centers means both terms cancel to zero exactly when the object is
    # inside, which is the same moment coverage reaches 100%.
    dx = max(0, rx1 - bx1) - max(0, bx2 - rx2)
    dy = max(0, ry1 - by1) - max(0, by2 - ry2)

    if abs(dx) / width < DEADZONE and abs(dy) / height < DEADZONE:
        return None

    # Correct the larger error first so the user is given one step at a time.
    # Panning the camera left pushes the object right in the frame, so the
    # camera always turns opposite to the object's required travel.
    if abs(dx) / width >= abs(dy) / height:
        return "Turn the camera left" if dx > 0 else "Turn the camera right"
    return "Tilt the camera up" if dy > 0 else "Tilt the camera down"
