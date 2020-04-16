import os
from geojson2vt.utils import current_dir, get_json
from geojson2vt.geojson2vt import geojson2vt
from geojson2vt.vt2geojson import vt2geojson


def test_vt2geojson():
    cur_dir = current_dir(__file__)
    data_path = os.path.join(cur_dir, f'fixtures/vt2geojson.geojson')
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
