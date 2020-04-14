import os
import json
import pprint

from geojson2vt.geojson2vt import geojson2vt
from geojson2vt.utils import current_dir, get_json


def test_small():
    cur_dir = current_dir(__file__)
    data_path = os.path.join(cur_dir, f'fixtures/small.json')
    file_path = os.path.join(cur_dir, f'fixtures/small_result.json')

    data = get_json(data_path)
    expected = get_json(file_path)

    geojson_vt = geojson2vt(data, {})
    geojson_vt.get_tile(14, 8617, 5752)

    geojson_vt_keys = sorted([str(k) for k in geojson_vt.tiles.keys()])
    expected_keys = sorted([str(k) for k in expected.keys()])

    assert geojson_vt_keys == expected_keys


def test_features():
    cur_dir = current_dir(__file__)
    data_path = os.path.join(cur_dir, f'fixtures/us-states.json')
    file_path = os.path.join(cur_dir, f'fixtures/feature_result.json')

    data = get_json(data_path)
    expected = get_json(file_path)

    geojson_vt = geojson2vt(data, {})
    features = geojson_vt.get_tile(7, 37, 48).get('features')

    feature_ids = [f.get('id') for f in features]
    expected_feature_ids = [f.get('id') for f in expected]

    assert feature_ids == expected_feature_ids
    assert features == expected


if __name__ == "__main__":
    test_features()
