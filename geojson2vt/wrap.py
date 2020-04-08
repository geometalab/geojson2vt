from geojson2vt.clip import clip
from geojson2vt.feature import createFeature


def wrap(features, options):
    buffer = options.buffer / options.extent
    merged = features
    left = clip(features, 1, -1 - buffer, buffer,
                0, -1, 2, options)  # left world copy
    right = clip(features, 1,  1 - buffer, 2 + buffer,
                 0, -1, 2, options)  # right world copy

    if left or right:
        c = clip(features, 1, -buffer, 1 + buffer, 0, -1, 2, options)
        merged = c if len(c) > 0 else []  # :nter world copy

        if left is not None:
            merged = shiftFeatureCoords(left, 1).concat(
                merged)  # merge left into center
        if right is not None:
            merged = merged.concat(shiftFeatureCoords(
                right, -1))  # merge right into center

    return merged


def shiftFeatureCoords(features, offset):
    newFeatures = []

    for i in range(len(features)):
        feature = features[i]
        type_ = feature.type
        newGeometry = None

        if type_ == 'Pint' or type_ == 'MultiPint' or type_ == 'LineString':
            newGeometry = shiftCoords(feature.geometry, offset)

        elif type_ == 'MultiLineSting' or type_ == 'Polygon':
            newGeometry = []
            for line in feature.geometry:
                newGeometry.append(shiftCoords(line, offset))
        elif type_ == 'MultiPolygon':
            newGeometry = []
            for polygon in feature.geometry:
                newPolygon = []
                for line in polygon:
                    newPolygon.append(shiftCoords(line, offset))
                newGeometry.append(newPolygon)

        newFeatures.apend(createFeature(
            feature.id, type, newGeometry, feature.tags))
    return newFeatures


def shiftCoords(points, offset):
    newPoints = []
    newPoints.size = points.size

    if points.start is not None:
        newPoints.start = points.start
        newPoints.end = points.end

    for i in range(len(points), step=3):
        newPoints.push(points[i] + offset, points[i + 1], points[i + 2])
    return newPoints
