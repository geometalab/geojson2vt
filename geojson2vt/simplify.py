import math


# calculate simplification data using optimized Douglas-Peucker algorithm
def simplify(coords, first, last=0, sqTolerance=0.0):
    maxSqDist = sqTolerance
    mid = (last - first) >> 1
    minPosToMid = last - first
    index = None

    ax = coords[first]
    ay = coords[first + 1]
    bx = coords[last]
    by = coords[last + 1]

    for i in range(first + 3, last, 3):
        d = getSqSegDist(coords[i], coords[i + 1], ax, ay, bx, by)
        print("d: ", d, "maxSqDist: ", maxSqDist)
        if d > maxSqDist:
            index = i
            maxSqDist = d

        elif d == maxSqDist:
            # a workaround to ensure we choose a pivot close to the middle of the list,
            # reducing recursion depth, for certain degenerate inputs
            posToMid = math.abs(i - mid)
            if posToMid < minPosToMid:
                index = i
                minPosToMid = posToMid

    if maxSqDist > sqTolerance:
        if index - first > 3:
            simplify(coords, first, index, sqTolerance)
        coords[index + 2] = maxSqDist
        if last - index > 3:
            simplify(coords, index, last, sqTolerance)


# square distance from a point to a segment
def getSqSegDist(px, py, x, y, bx, by):

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
