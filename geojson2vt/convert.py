import math

from geojson2vt.simplify import simplify
from geojson2vt.feature import Slice, create_feature

# converts GeoJSON feature into an intermediate projected JSON vector format with simplification data


def convert(data, options):
    features = []
    if data.get('type') == 'FeatureCollection':
        for i in range(len(data.get('features'))):
            convert_feature(features, data.get('features')[i], options, i)
    elif data.get('type') == 'Feature':
        convert_feature(features, data, options)
    else:
        # single geometry or a geometry collection
        convert_feature(features, {"geometry": data}, options)
    return features


def convert_feature(features, geojson, options, index=None):
    if geojson.get('geometry', None) is None:
        return

    coords = geojson.get('geometry').get('coordinates')
    type_ = geojson.get('geometry').get('type')
    tolerance = math.pow(options.get(
        'tolerance') / ((1 << options.get('maxZoom')) * options.get('extent')), 2)
    geometry = Slice([])
    id_ = geojson.get('id')
    if options.get('promoteId', None) is not None and geojson.get('properties', None) is not None and 'promoteId' in geojson.get('properties'):
        id_ = geojson['properties'][options.get('promoteId')]
    elif options.get('generateId', False):
        id_ = index if index is not None else 0

    if type_ == 'Point':
        convert_point(coords, geometry)
    elif type_ == 'MultiPoint':
        for p in coords:
            convert_point(p, geometry)
    elif type_ == 'LineString':
        convert_line(coords, geometry, tolerance, False)
    elif type_ == 'MultiLineString':
        if options.get('lineMetrics'):
            # explode into linestrings to be able to track metrics
            for line in coords:
                geometry = Slice([])
                convert_line(line, geometry, tolerance, False)
                features.append(create_feature(id_, 'LineString',
                                               geometry, geojson.get('properties')))
            return
        else:
            convert_lines(coords, geometry, tolerance, False)
    elif type_ == 'Polygon':
        convert_lines(coords, geometry, tolerance, True)
    elif type_ == 'MultiPolygon':
        for polygon in coords:
            newPolygon = []
            convert_lines(polygon, newPolygon, tolerance, True)
            geometry.append(newPolygon)
    elif type_ == 'GeometryCollection':
        for singleGeometry in geojson['geometry']['geometries']:
            convert_feature(features, {
                "id": str(id_),
                "geometry": singleGeometry,
                "properties": geojson.get('properties')
            }, options, index)
        return
    else:
        raise Exception('Input data is not a valid GeoJSON object.')

    features.append(create_feature(
        id_, type_, geometry, geojson.get('properties')))


def convert_point(coords, out):
    out.append(project_x(coords[0]))
    out.append(project_y(coords[1]))
    out.append(0)


def convert_line(ring, out, tolerance, isPolygon):
    x0, y0 = None, None
    size = 0

    for j in range(len(ring)):
        x = project_x(ring[j][0])
        y = project_y(ring[j][1])

        out.append(x)
        out.append(y)
        out.append(0)

        if j > 0:
            if isPolygon:
                size += (x0 * y - x * y0) / 2  # area
            else:
                size += math.sqrt(math.pow(x - x0, 2) +
                                  math.pow(y - y0, 2))  # length
        x0 = x
        y0 = y

    last = len(out) - 3
    out[2] = 1
    simplify(out, 0, last, tolerance)
    out[last + 2] = 1.

    out.size = abs(size)
    out.start = 0.
    out.end = out.size


def convert_lines(rings, out, tolerance, isPolygon):
    for i in range(len(rings)):
        geom = Slice([])
        convert_line(rings[i], geom, tolerance, isPolygon)
        out.append(geom)


def project_x(x):
    return x / 360. + 0.5


def project_y(y):
    sin = math.sin(y * math.pi / 180.)
    if sin == 1.:
        return 0.
    if sin == -1.:
        return 1.
    y2 = 0.5 - 0.25 * math.log((1. + sin) / (1. - sin)) / math.pi
    return 0 if y2 < 0. else (1. if y2 > 1. else y2)
