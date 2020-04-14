import os
import json
import pprint

from geojson2vt.geojson2vt import geojson2vt


def test_samll():
    data = get_json('small.json')
    geojson_vt = geojson2vt(data, {})
    expected = get_json('small_result.json')
    geojson_vt.get_tile(14, 8617, 5752)

    geojson_vt_keys = sorted([str(k) for k in geojson_vt.tiles.keys()])
    expected_keys = sorted([str(k) for k in expected.keys()])

    assert geojson_vt_keys == expected_keys

def test_features():
    data = get_json('us-states.json')
    expected = get_json('feature_result.json')
    
    geojson_vt = geojson2vt(data, {})
    features = geojson_vt.get_tile(7, 37, 48).get('features')

    feature_ids = [f.get('id') for f in features]
    expected_feature_ids = [f.get('id') for f in expected]
    # const index = geojsonvt(getJSON('us-states.json'), {debug: 2});
    # const features = index.getTile(7, 37, 48).features;
    assert feature_ids == expected_feature_ids
    #assert features == expected

def get_json(file_name):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    fixtures_path = os.path.join(dir_path, 'fixtures')
    file_path = os.path.join(fixtures_path, file_name)
    data = None
    with open(file_path) as json_file:
        data = json.load(json_file)
    return data


if __name__ == "__main__":
    test_features()
