import math

from geojson2vt.clip import clip, Slice

geom1 = [0., 0., 0., 50., 0., 0., 50., 10., 0., 20., 10., 0., 20., 20., 0., 30., 20., 0., 30., 30.,
         0., 50., 30., 0., 50., 40., 0., 25., 40., 0., 25., 50., 0., 0., 50., 0., 0., 60., 0., 25., 60., 0.]
geom2 = [0, 0, 0, 50, 0, 0, 50, 10, 0, 0, 10, 0]


def test_clips_polylines():
    clipped = clip([
        {'geometry': geom1, 'type': 'LineString', 'tags': 1,
            'minX': 0, 'minY': 0, 'maxX': 50, 'maxY': 60},
        {'geometry': geom2, 'type': 'LineString', 'tags': 2,
            'minX': 0, 'minY': 0, 'maxX': 50, 'maxY': 10}
    ], 1, 10, 40, 0, float('-inf'), float('inf'), {})

    expected = [
        {
            'id': None,
            'type': 'MultiLineString',
            'geometry': [
                [10, 0, 1, 40, 0, 1],
                [40, 10, 1, 20, 10, 0, 20, 20, 0, 30, 20, 0, 30, 30, 0, 40, 30, 1],
                [40, 40, 1, 25, 40, 0, 25, 50, 0, 10, 50, 1],
                [10, 60, 1, 25, 60, 0]
            ],
            'tags': 1,
            'minX': 10,
            'minY': 0,
            'maxX': 40,
            'maxY': 60
        },
        {
            'id': None,
            'type':
            'MultiLineString',
            'geometry': [
                [10, 0, 1, 40, 0, 1],
                [40, 10, 1, 10, 10, 1]
            ],
            'tags': 2,
            'minX': 10,
            'minY': 0,
            'maxX': 40,
            'maxY': 10
        }
    ]
    assert clipped == expected


def test_clips_line_metrics_on():
    geom = Slice(geom1)
    geom.size = 0
    for i in range(0, len(geom)-3, 3):
        dx = geom[i + 3] - geom[i]
        dy = geom[i + 4] - geom[i + 1]
        geom.size += math.sqrt(dx * dx + dy * dy)
    geom.start = 0
    geom.end = geom.size

    clipped = clip([{'geometry': geom, 'type': 'LineString', 'minX': 0, 'minY': 0, 'maxX': 50, 'maxY': 60}],
                   1, 10, 40, 0, float('-inf'), float('inf'), {'lineMetrics': True})

    expected = [[10.0, 40.0], [70.0, 130.0], [160.0, 200.0], [230.0, 245.0]]
    for c, e in zip(clipped, expected):
        assert [c.get('geometry').start, c.get('geometry').end] == e


def closed(geometry):
    geometry += geometry[0:3]
    return geometry


def test_clips_poygons():
    clipped = clip([
        {'geometry': closed(geom1), 'type': 'Polygon', 'tags': 1,
         'minX': 0, 'minY': 0, 'maxX': 50, 'maxY': 60},
        {'geometry': closed(geom2), 'type': 'Polygon', 'tags': 2,
         'minX': 0, 'minY': 0, 'maxX': 50, 'maxY': 10}
    ], 1, 10, 40, 0, float('-inf'), float('inf'), {})

    expected = [
        {'id': None, 'type': 'Polygon', 'geometry': [[10., 0., 1., 40., 0., 1., 40., 10., 1., 20., 10., 0., 20., 20., 0., 30., 20., 0., 30., 30., 0., 40., 30., 1., 40., 40.,
                                                      1., 25., 40., 0., 25., 50., 0., 10., 50., 1., 10., 60., 1., 25., 60., 0., 10., 24., 1., 10., 0., 1.]], 'tags': 1, 'minX': 10, 'minY': 0, 'maxX': 40, 'maxY': 60},
        {'id': None, 'type': 'Polygon', 'geometry': [
            [10., 0., 1., 40., 0., 1., 40., 10., 1., 10., 10., 1., 10., 0., 1.]], 'tags': 2,  'minX': 10, 'minY': 0, 'maxX': 40, 'maxY': 10}
    ]
    for c, e in zip(clipped, expected):
        assert c.get('geometry') == e.get('geometry')

def test_clips_points():
    clipped = clip([
        {'geometry': geom1, 'type': 'MultiPoint', 'tags': 1, 'minX': 0, 'minY': 0, 'maxX': 50, 'maxY': 60},
        {'geometry': geom2, 'type': 'MultiPoint', 'tags': 2, 'minX': 0, 'minY': 0, 'maxX': 50, 'maxY': 10}
    ], 1, 10, 40, 0, float('-inf'), float('inf'), {})

    assert clipped ==[{'id': None, 'type': 'MultiPoint', 'geometry': [20,10,0,20,20,0,30,20,0,30,30,0,25,40,0,25,50,0,25,60,0], 'tags': 1, 'minX': 20, 'minY': 10, 'maxX': 30, 'maxY': 60}]
