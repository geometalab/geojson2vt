import math

geometry_types = {
    0: 'Unknown',
    1: 'Point',
    2: 'LineString',
    3: 'Polygon',
    4: 'MultiLineString'
}


def vt2geojson(tile, extent=4096):
    features = tile.get('features', [])
    size = extent * 2 ** tile.get('z')
    x0 = extent * tile.get('x')
    y0 = extent * tile.get('y')

    geojson_features = [vt_feature2geojson_feature(feature, size, x0, y0)
                        for feature in features]

    return {
        "type": "FeatureCollection",
        "features": geojson_features
    }


def vt_feature2geojson_feature(feature, size, x0, y0):
    def project_one(p_x, p_y):
        y2 = 180. - (p_y + y0) * 360. / size
        lng = (p_x + x0) * 360. / size - 180.
        lat = 360. / math.pi * math.atan(math.exp(y2 * math.pi / 180.)) - 90.
        return [lng, lat]

    def project(coords):
        if all(isinstance(coord, int) or isinstance(coord, float) for coord in coords):
            assert len(coords) == 2
            return project_one(coords[0], coords[1])
        return [project(cord) for cord in coords]

    coords = project(feature['geometry'])

    return {
        "type": "Feature",
        "geometry": {
            "type": geometry_types[feature['type']],
            "coordinates": coords if len(coords) > 1 else coords[0]
        },
        "properties": feature.get('tags', {})
    }
