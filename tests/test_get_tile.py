import os
import json

from geojson2vt.main import geojsonvt

square = [{
    'geometry': [[[-64, 4160], [-64, -64], [4160, -64], [4160, 4160], [-64, 4160]]],
    'type': 3,
    'tags': {'name': 'Pennsylvania', 'density': 284.3},
    'id': '42'
}]

def test_get_tile():

    index = geojsonvt(get_json('us-states.json'), {'debug': 2})

    assert index.get_tile(7, 37, 48).get('features') == get_json('us-states-z7-37-48.json')
    assert index.get_tile('7', '37', '48').get('features') == get_json('us-states-z7-37-48.json')

    assert index.get_tile(9, 148, 192).get('feature') == square
    assert index.get_tile(11, 800, 400) == None
    assert index.get_tile(-5, 123.25, 400.25) == None
    assert index.get_tile(25, 200, 200) == None


    assert index.total == 37

# test('getTile: unbuffered tile left/right edges', (t) => {
#     index = geojsonvt({
#         type: 'LineString',
#         coordinates: [[0, 90], [0, -90]]
#     }, {
#         buffer: 0
#     });

#     t.same(index.getTile(2, 1, 1), null);
#     t.same(index.getTile(2, 2, 1).features, [{geometry: [[[0, 0], [0, 4096]]], type: 2, tags: null}]);
#     t.end();
# });

# test('getTile: unbuffered tile top/bottom edges', (t) => {
#     index = geojsonvt({
#         type: 'LineString',
#         coordinates: [[-90, 66.51326044311188], [90, 66.51326044311188]]
#     }, {
#         buffer: 0
#     });

#     t.same(index.getTile(2, 1, 0).features, [{geometry: [[[0, 4096], [4096, 4096]]], type: 2, tags: null}]);
#     t.same(index.getTile(2, 1, 1).features, []);
#     t.end();
# });

# test('getTile: polygon clipping on the boundary', (t) => {
#     index = geojsonvt({
#         type: 'Polygon',
#         coordinates: [[
#             [42.1875, 57.32652122521708],
#             [47.8125, 57.32652122521708],
#             [47.8125, 54.16243396806781],
#             [42.1875, 54.16243396806781],
#             [42.1875, 57.32652122521708]
#         ]]
#     }, {
#         buffer: 1024
#     });

#     t.same(index.getTile(5, 19, 9).features, [{
#         geometry: [[[3072, 3072], [5120, 3072], [5120, 5120], [3072, 5120], [3072, 3072]]],
#         type: 3,
#         tags: null
#     }]);

#     t.end();
# });

def get_json(file_name):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    fixtures_path = os.path.join(dir_path,'fixtures')
    file_path = os.path.join(fixtures_path, file_name)
    with open(file_path) as json_file:
        data = json.load(json_file)
        return data