Usage
-----
geojson2vt
**********
.. code:: python

    # build an initial index of tiles
    tile_index = geojson2vt(geojson, {})

    # request a particular tile
    features = tile_index.get_tile(z, x, y).get('features')

    # show an array of tile coordinates created so far
    print(tile_index.tile_coords) # [{'z': 0, 'x': 0, 'y': 0}, ...]

You can fine-tune the results with an options object,
although the defaults are sensible and work well for most use cases.

By default, tiles at zoom levels above ``indexMaxZoom`` are generated on the fly, but you can pre-generate all possible tiles for data by setting ``indexMaxZoom`` and ``maxZoom`` to the same value, setting ``indexMaxPoints`` to 0, and then accessing the resulting tile coordinates from the ``tile_coords`` property of ``tile_index``.

The ``promoteId`` and ``generateId`` options ignore existing ``id`` values on the feature objects.

geojson2vt only operates on zoom levels up to 24.


.. code:: python

    tile_index = geojson2vt(data, {
        'maxZoom': 14,  # max zoom to preserve detail on; can't be higher than 24
        'tolerance': 3, # simplification tolerance (higher means simpler)
        'extent': 4096, # tile extent (both width and height)
        'buffer': 64,   # tile buffer on each side
        'lineMetrics': False, # whether to enable line metrics tracking for LineString/MultiLineString features
        'promoteId': None,    # name of a feature property to promote to feature.id. Cannot be used with `generateId`
        'generateId': False,  # whether to generate feature ids. Cannot be used with `promoteId`
        'indexMaxZoom': 5,       # max zoom in the initial tile index
        'indexMaxPoints': 100000 # max number of points per tile in the index
    }, logging.INFO)
    


vt2geojson
**********
.. code:: python

    # build an initial index of tiles
    tile_index = geojson2vt(geojson_data, {})

    # get a specific tile
    vt_tile = tile_index.get_tile(z, x, y)

    # convert a specific vector tile to GeoJSON
    geojson = vt2geojson(vt_tile)


Acknowledgements
----------------

All the credit belongs to the collaborators of JS GeoJSON-VT.