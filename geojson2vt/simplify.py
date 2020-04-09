import math


# calculate simplification data using optimized Douglas-Peucker algorithm
def simplify(coords, first, last=0, sq_tolerance=0.0):
    max_sq_dist = sq_tolerance
    mid = (last - first) >> 1
    min_pos_to_mid = last - first
    index = None

    ax = coords[first]
    ay = coords[first + 1]
    bx = coords[last]
    by = coords[last + 1]

    for i in range(first + 3, last, 3):
        d = get_sq_seg_dist(coords[i], coords[i + 1], ax, ay, bx, by)
        if d > max_sq_dist:
            index = i
            max_sq_dist = d

        elif d == max_sq_dist:
            # a workaround to ensure we choose a pivot close to the middle of the list,
            # reducing recursion depth, for certain degenerate inputs
            pos_to_mid = abs(i - mid)
            if pos_to_mid < min_pos_to_mid:
                index = i
                min_pos_to_mid = pos_to_mid

    if max_sq_dist > sq_tolerance:
        if index - first > 3:
            simplify(coords, first, index, sq_tolerance)
        coords[index + 2] = max_sq_dist
        if last - index > 3:
            simplify(coords, index, last, sq_tolerance)


# square distance from a point to a segment
def get_sq_seg_dist(px, py, x, y, bx, by):

    dx = bx - x
    dy = by - y

    if dx != 0 or dy != 0:

        t = ((px - x) * dx + (py - y) * dy) / (dx * dx + dy * dy)

        if t > 1:
            x = bx
            y = by

        elif (t > 0):
            x += dx * t
            y += dy * t

    dx = px - x
    dy = py - y

    return dx * dx + dy * dy
