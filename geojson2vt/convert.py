import math

from geojson2vt.simplify import simplify
from geojson2vt.feature import createFeature

# converts GeoJSON feature into an intermediate projected JSON vector format with simplification data

def convert(data, options):
    features = []
    if data.type == 'FeatureCollection':
        for i in range(len(data.feature)):
            convertFeature(features, data.features[i], options, i)
    elif data.type == 'Feature':
        convertFeature(features, data, options)
    else:
        # single geometry or a geometry collection
        convertFeature(features, {"geometry": data}, options)
    return features

def convertFeature(features, geojson, options, index):
    if geojson.geometry is None:
         return

    coords = geojson.geometry.coordinates
    type_ = geojson.geometry.type
    tolerance = math.pow(options.tolerance / ((1 << options.maxZoom) * options.extent), 2)
    geometry = []
    id = geojson.id
    if options.promoteId is not None:
        id = geojson.properties[options.promoteId]
    elif options.generateId is not None:
        id = index if index is not None else 0
    
    if type_ == 'Point':
        convertPoint(coords, geometry)
    elif type_ == 'MultiPoint':
        for p in coords:
            convertPoint(p, geometry)
    elif type_ == 'LineString':
        convertLine(coords, geometry, tolerance, False)
    elif type_ == 'MultiLineString':
        if options.lineMetrics:
            # explode into linestrings to be able to track metrics
            for line in coords:
                geometry = []
                convertLine(line, geometry, tolerance, False)
                features.push(createFeature(id, 'LineString', geometry, geojson.properties))
            return
        else:
            convertLines(coords, geometry, tolerance, False)
    elif type_ == 'Polygon':
        convertLines(coords, geometry, tolerance, True)
    elif type_ == 'MultiPolygon':
        for polygon in coords:
            newPolygon = []
            convertLines(polygon, newPolygon, tolerance, True)
            geometry.push(newPolygon)
    elif type_ == 'GeometryCollection':
        for singleGeometry in geojson.geometry.geometries:
            convertFeature(features, {
                "id": id,
                "geometry": singleGeometry,
                "properties": geojson.properties
            }, options, index)
        return
    else:
        raise Exception('Input data is not a valid GeoJSON object.')

    features.append(createFeature(id, type_, geometry, geojson.properties))

def convertPoint(coords, out):
    out.append(projectX(coords[0]), projectY(coords[1]), 0)

def convertLine(ring, out, tolerance, isPolygon):
    x0, y0 = None, None
    size = 0

    for j in range(len(ring)):
        x = projectX(ring[j][0]);
        y = projectY(ring[j][1]);

        out.append(x, y, 0)

        if j > 0:
            if isPolygon:
                size += (x0 * y - x * y0) / 2; # area
            else:
                size += math.sqrt(math.pow(x - x0, 2) + math.pow(y - y0, 2)); # length
        x0 = x
        y0 = y

    last = len(out) - 3
    out[2] = 1
    simplify(out, 0, last, tolerance)
    out[last + 2] = 1

    out.size = math.abs(size)
    out.start = 0
    out.end = out.size

def convertLines(rings, out, tolerance, isPolygon):
    for i in range(len(rings)):
        geom = []
        convertLine(rings[i], geom, tolerance, isPolygon)
        out.append(geom)

def projectX(x):
    return x / 360 + 0.5

def projectY(y):
    sin = math.sin(y * math.PI / 180)
    y2 = 0.5 - 0.25 * math.log((1 + sin) / (1 - sin)) / math.PI
    return 0 if y2 < 0 else (1 if y2 > 1 else y2)