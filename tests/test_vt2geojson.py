import os
from geojson2vt.utils import current_dir, get_json
from geojson2vt.geojson2vt import geojson2vt
from geojson2vt.vt2geojson import vt2geojson


def test_vt2geojson_line_string():
    cur_dir = current_dir(__file__)
    data_path = os.path.join(cur_dir, f'fixtures/linestring.geojson')
    geojson = get_json(data_path)
    expected = {
        "type": "FeatureCollection",
        "features": [
            {"type": "Feature",
             "geometry": {
                "type": "LineString",
                "coordinates": [
                    [9.333594851195812, 47.11501442877534],
                    [9.33286428451538, 47.11409674087989]
                ]
             },
             "properties": {}
             }
        ]
    }

    z, x, y = 18, 137868, 92080
    tile_index = geojson2vt(
        geojson, {'maxZoom': z, 'indexMaxZoom': z, 'indexMaxPoints': 0})

    vt_tile = tile_index.get_tile(z, x, y)

    result = vt2geojson(vt_tile)

    assert result == expected

def test_vt2geojson_multi():
    cur_dir = current_dir(__file__)
    data_path = os.path.join(cur_dir, f'fixtures/multi.geojson')
    geojson = get_json(data_path)
    x, y, z = 2153, 1438, 12
    expected = {'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'geometry': {'type': 'Polygon', 'coordinates': [[[9.31065559387207, 47.12633021376186], [9.303703308105469, 47.12142456895782], [9.317779541015625, 47.11764282567128], [9.317779541015625, 47.12698718541262], [9.31065559387207, 47.12633021376186]]]}, 'properties': {}}, {'type': 'Feature', 'geometry': {'type': 'Point', 'coordinates': [9.303016662597656, 47.12673899707599]}, 'properties': {}}]}
    
    tile_index = geojson2vt(
        geojson, {'maxZoom': z, 'indexMaxZoom': z, 'indexMaxPoints': 0})
    vt_tile = tile_index.get_tile(z, x, y)
    
    result = vt2geojson(vt_tile)

    assert result == expected