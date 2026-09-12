Region = tuple[int, int, int, int]


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
