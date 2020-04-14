import os
import json

from geojson2vt.geojson2vt import geojson2vt

square = [{
    'geometry': [[[-64., 4160.], [-64., -64.], [4160., -64.], [4160., 4160.], [-64., 4160.]]],
    'type': 3,
    'tags': {'name': 'Pennsylvania', 'density': 284.3},
    'id': '42'
}]


def test_get_tile():
    data = get_json('us-states.json')
    geojson_vt = geojson2vt(data, {})

    features = geojson_vt.get_tile('7', '37', '48').get(
        'features')
    expected = get_json('us-states-z7-37-48.json')
    assert features == expected
    assert geojson_vt.get_tile(9, 148, 192).get('features') == square
    assert geojson_vt.get_tile(11, 800, 400) == None
    assert geojson_vt.get_tile(-5, 123.25, 400.25) == None
    assert geojson_vt.get_tile(25, 200, 200) == None
    assert geojson_vt.total == 37


def test_get_tile_unbuffered():
    geojson_vt = geojson2vt({
        'type': 'LineString',
        'coordinates': [[0., 90.], [0., -90.]]
    }, {
        'buffer': 0
    })
    assert geojson_vt.get_tile(2, 1, 1) == None
    assert geojson_vt.get_tile(2, 2, 1).get('features') == [
        {'geometry': [[[0., 0.], [0., 4096.]]], 'type': 2, 'tags': None}]


def test_get_tile_unbuffered_edges():
    geojson_vt = geojson2vt({
        'type': 'LineString',
        'coordinates': [[-90.0, 66.51326044311188], [90.0, 66.51326044311188]]
    }, {
        'buffer': 0
    })
    assert geojson_vt.get_tile(2, 1, 0).get('features') == [{'geometry': [
        [[0.0, 4096.0], [4096.0, 4096.0]]], 'type': 2, 'tags': None}]
    assert geojson_vt.get_tile(2, 1, 1).get('features') == []


def test_get_tile_polygon_clipping():
    geojson_vt = geojson2vt({
        'type': 'Polygon',
        'coordinates': [[
            [42.1875, 57.32652122521708],
            [47.8125, 57.32652122521708],
            [47.8125, 54.16243396806781],
            [42.1875, 54.16243396806781],
            [42.1875, 57.32652122521708]
        ]]
    }, {
        'buffer': 1024
    })
    assert geojson_vt.get_tile(5, 19, 9).get('features') == [{
        'geometry': [[[3072., 3072.], [5120., 3072.], [5120., 5120.], [3072., 5120.], [3072., 3072.]]],
        'type': 3,
        'tags': None
    }]


def get_json(file_name):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    fixtures_path = os.path.join(dir_path, 'fixtures')
    file_path = os.path.join(fixtures_path, file_name)
    data = None
    with open(file_path) as json_file:
        data = json.load(json_file)
        change_int_coords_to_float(data)
    return data


def change_int_coords_to_float(data):
    if isinstance(data, list):
        walk_list(data)
    else:
        walk_dict(data)


def walk_dict(tree):
    for key, value in tree.items():
        if isinstance(value, dict):
            walk_dict(value)
        if isinstance(value, list):
            walk_list(value)


def walk_list(lst):
    if len(lst) == 0:
        return
    if isinstance(lst[0], list):
        for l in lst:
            walk_list(l)
    elif isinstance(lst[0], int):
        for i in range(len(lst)):
            lst[i] = float(lst[i])
    elif isinstance(lst[0], dict):
        for i in range(len(lst)):
            walk_dict(lst[i])


if __name__ == "__main__":
    test_get_tile()
