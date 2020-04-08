import math
from geojson2vt.feature import createFeature, Slice


""" clip features between two vertical or horizontal axis-parallel lines:
 *     |        |
 *  ___|___     |     /
 * /   |   \____|____/
 *     |        |
 *
 * k1 and k2 are the line coordinates
 * axis: 0 for x, 1 for y
 * minAll and maxAll: minimum and maximum coordinate value for all features
 """


def clip(features, scale, k1, k2, axis, minAll, maxAll, options):
    k1 /= scale
    k2 /= scale

    if minAll >= k1 and maxAll < k2:
        return features  # trivial accept
    elif maxAll < k1 or minAll >= k2:
        return None  # trivial reject

    clipped = []

    for feature in features:
        geometry = feature.get('geometry')
        type_ = feature.get('type')

        min_ = feature.get('minX') if axis == 0 else feature.get('minY')
        max_ = feature.get('maxX') if axis == 0 else feature.get('maxY')

        if min_ >= k1 and max_ < k2:  # trivial accept
            clipped.append(feature)
            continue
        elif max_ < k1 or min_ >= k2:  # trivial reject
            continue

        newGeometry = []

        if type_ == 'Point' or type_ == 'MultiPoint':
            clipPoints(geometry, newGeometry, k1, k2, axis)
        elif type_ == 'LineString':
            clipLine(geometry, newGeometry, k1, k2,
                     axis, False, options.get('lineMetrics'))
        elif type_ == 'MultiLineString':
            clipLines(geometry, newGeometry, k1, k2, axis, False)
        elif type_ == 'Polygon':
            clipLines(geometry, newGeometry, k1, k2, axis, True)
        elif type_ == 'MultiPolygon':
            for polygon in geometry:
                newPolygon = []
                clipLines(polygon, newPolygon, k1, k2, axis, True)
                if len(newPolygon) > 0:
                    newGeometry.append(newPolygon)

        if len(newGeometry) > 0:
            if options.get('lineMetrics') and type_ == 'LineString':
                for line in newGeometry:
                    clipped.append(createFeature(
                        feature.get('id'), type_, line, feature.get('tags')))
                continue

            if type_ == 'LineString' or type_ == 'MultiLineString':
                if len(newGeometry) == 1:
                    type_ = 'LineString'
                    newGeometry = newGeometry[0]
                else:
                    type_ = 'MultiLineString'

            if type_ == 'Point' or type_ == 'MultiPoint':
                type_ = 'Point' if len(newGeometry) == 3 else 'MultiPoint'

            clipped.append(createFeature(
                feature.get('id'), type_, newGeometry, feature.get('tags')))

    return clipped if len(clipped) > 0 else None


def clipPoints(geom, newGeom, k1, k2, axis):
    for i in range(0, len(geom), 3):
        a = geom[i + axis]
        if a >= k1 and a <= k2:
            addPoint(newGeom, geom[i], geom[i + 1], geom[i + 2])


def clipLine(geom, newGeom, k1, k2, axis, isPolygon, trackMetrics):
    slice_ = newSlice(geom)
    intersect = intersectX if axis == 0 else intersectY
    l = geom.start
    segLen, t = None, None

    for i in range(0, len(geom) - 3, 3):
        ax = geom[i]
        ay = geom[i + 1]
        az = geom[i + 2]
        bx = geom[i + 3]
        by = geom[i + 4]
        a = ax if axis == 0 else ay
        b = bx if axis == 0 else by
        exited = False

        if trackMetrics:
            segLen = math.sqrt(math.pow(ax - bx, 2) + math.pow(ay - by, 2))

        if a < k1:
            # ---|-->  | (line enters the clip region from the left)
            if b > k1:
                t = intersect(slice_, ax, ay, bx, by, k1)
                if trackMetrics:
                    slice_.start = l + segLen * t
        elif a > k2:
            # |  <--|--- (line enters the clip region from the right)
            if b < k2:
                t = intersect(slice_, ax, ay, bx, by, k2)
                if trackMetrics:
                    slice_.start = l + segLen * t
        else:
            addPoint(slice_, ax, ay, az)
        if b < k1 and a >= k1:
            # <--|---  | or <--|-----|--- (line exits the clip region on the left)
            t = intersect(slice_, ax, ay, bx, by, k1)
            exited = True
        if b > k2 and a <= k2:
            # |  ---|--> or ---|-----|--> (line exits the clip region on the right)
            t = intersect(slice_, ax, ay, bx, by, k2)
            exited = True

        if not isPolygon and exited:
            if trackMetrics:
                slice_.end = l + segLen * t
            newGeom.append(slice_)
            slice_ = newSlice(geom)

        if trackMetrics:
            l += segLen

    # add the last point
    last = len(geom) - 3
    ax = geom[last]
    ay = geom[last + 1]
    az = geom[last + 2]
    a = ax if axis == 0 else ay
    if a >= k1 and a <= k2:
        addPoint(slice_, ax, ay, az)

    # close the polygon if its endpoints are not the same after clipping
    last = len(slice_) - 3
    if isPolygon and last >= 3 and (slice_[last] != slice_[0] or slice_[last + 1] != slice_[1]):
        addPoint(slice_, slice_[0], slice_[1], slice_[2])

    # add the final slice
    if len(slice_) > 0:
        newGeom.append(slice_)


def newSlice(line):
    # slice_ = []
    # print("newSlice: ", str(line))
    slice_ = Slice([])
    slice_.size = len(line)
    slice_.start = 0 #line.start
    slice_.end = len(line) -1
    return slice_


def clipLines(geom, newGeom, k1, k2, axis, isPolygon):
    for line in geom:
        clipLine(line, newGeom, k1, k2, axis, isPolygon, False)


def addPoint(out, x, y, z):
    #out.append(x, y, z)
    out.append(x)
    out.append(y)
    out.append(z)


def intersectX(out, ax, ay, bx, by, x):
    t = (x - ax) / (bx - ax)
    addPoint(out, x, ay + (by - ay) * t, 1)
    return t


def intersectY(out, ax, ay, bx, by, y):
    t = (y - ay) / (by - ay)
    addPoint(out, ax + (bx - ax) * t, y, 1)
    return t
