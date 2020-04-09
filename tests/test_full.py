import os
import json

import pytest

from geojson2vt.geojson2vt import geojson2vt


@pytest.mark.parametrize("input_file,expected_file,options", [
    ('us-states.json', 'us-states-tiles.json',
     {'indexMaxZoom': 7, 'indexMaxPoints': 200}),
    # ('dateline.json', 'dateline-tiles.json',
    #  {'indexMaxZoom': 0, 'indexMaxPoints': 10000}),
    # ('dateline.json', 'dateline-metrics-tiles.json',
    #  {'indexMaxZoom': 0, 'indexMaxPoints': 10000, 'lineMetrics': True}),
    # ('feature.json', 'feature-tiles.json',
    #  {'indexMaxZoom': 0, 'indexMaxPoints': 10000}),
    # ('collection.json', 'collection-tiles.json',
    #  {'indexMaxZoom': 0, 'indexMaxPoints': 10000}),
    # ('single-geom.json', 'single-geom-tiles.json',
    #  {'indexMaxZoom': 0, 'indexMaxPoints': 10000}),
    # ('ids.json', 'ids-promote-id-tiles.json',
    #  {'indexMaxZoom': 0, 'promoteId': 'prop0'}),
    # ('ids.json', 'ids-generate-id-tiles.json',
    #  {'indexMaxZoom': 0, 'generateId': True})
])
def test_tiles(input_file, expected_file, options):
    tiles = gen_tiles(get_json(input_file), options)
    for t, j in zip(tiles.items(), get_json(expected_file).items()):
        assert t == j
        break


def test_empty_gejson():
    result = gen_tiles(get_json('empty.json'), {})
    assert {} == result


def test_none_geometry():
    assert {} == gen_tiles(get_json('feature-null-geometry.json'), {})


def test_invalid_geo_json():
    with pytest.raises(Exception):
        gen_tiles({'type': 'Pologon'}, {})


def gen_tiles(data, options):
    opt = options.copy()
    opt['indexMaxZoom'] = 0
    opt['indexMaxPoints'] = 10000

    geoJsonVt = geojson2vt(data, opt)

    output = {}

    for id_ in geoJsonVt.tiles:
        tile = geoJsonVt.tiles[id_]
        z = tile.get('z')
        output[f'z{z}-{tile.get("x")}-{tile.get("y")}'] = geoJsonVt.get_tile(
            z, tile.get('x'), tile.get('y')).get('features')
    return output


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
