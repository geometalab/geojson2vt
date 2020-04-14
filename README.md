# geojson2vt
Converts GeoJSON to vector tiles

### Usage

```python
# build an initial index of tiles
tile_index = geojsonvt(geo_json)

# request a particular tile
features = tileIndex.get_tile(z, x, y).get('features')

# show an array of tile coordinates created so far
print(tileIndex.tileCoords) # [{z: 0, x: 0, y: 0}, ...]
```

### Options

You can fine-tune the results with an options object,
although the defaults are sensible and work well for most use cases.

```python
tile_index = geojsonvt(data, {
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
```