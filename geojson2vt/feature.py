import math


def createFeature(id, type_, geom, tags):
    test = {"test": 10, "aber": "ud"}
    feature = {
        "id": None if id is None else id,
        "type": type_,
        "geometry": geom,
        "tags": tags,
        "minX": float('inf'),
        "minY": float('inf'),
        "maxX": float('-inf'),
        "maxY": float('-inf')
    }

    if type_ == 'Point' or type_ == 'MultiPoint' or type_ == 'LineString':
        calcLineBBox(feature, geom)

    elif type_ == 'Polygon':
        # the outer ring(ie[0]) contains all inner rings
        calcLineBBox(feature, geom[0])
    elif type_ == 'MultiLineString':
        for line in geom:
            calcLineBBox(feature, line)
    elif type == 'MultiPolygon':
        for polygon in geom:
            # the outer ring(ie[0]) contains all inner rings
            calcLineBBox(feature, polygon[0])

    return feature


def calcLineBBox(feature, geom):
    for i in range(len(geom), step=3):
        feature.minX = math.min(feature.minX, geom[i])
        feature.minY = math.min(feature.minY, geom[i + 1])
        feature.maxX = math.max(feature.maxX, geom[i])
        feature.maxY = math.max(feature.maxY, geom[i + 1])
