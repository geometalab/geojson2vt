from datetime import datetime

from geojson2vt.convert import convert
from geojson2vt.clip import clip
from geojson2vt.wrap import wrap
from geojson2vt.transform import transform
from geojson2vt.tile import createTile

defaultOptions = {
    "maxZoom": 14,            # max zoom to preserve detail on
    "indexMaxZoom": 5,        # max zoom in the tile index
    "indexMaxPoints": 100000,  # max number of points per tile in the tile index
    "tolerance": 3,           # simplification tolerance (higher means simpler)
    "extent": 4096,           # tile extent
    "buffer": 64,             # tile buffer on each side
    "lineMetrics": False,     # whether to calculate line metrics
    "promoteId": None,        # name of a feature property to be promoted to feature.id
    "generateId": False,      # whether to generate feature ids. Cannot be used with promoteId
    "debug": 0                # logging level (0, 1 or 2)
}


class GeoJSONVT:
    def __init__(self, data, options):
        super().__init__()
        # options = self.options = extend(Object.create(defaultOptions), options)

        debug = options.debug

        start = None
        if debug:
            print('preprocess data')
            start = datetime.now()

        if options.maxZoom < 0 or options.maxZoom > 24:
            raise Exception('maxZoom should be in the 0-24 range')
        if options.promoteId is not None and options.generateId is not None:
            raise Exception(
                'promoteId and generateId cannot be used together.')

        # projects and adds simplification info
        features = convert(data, options)

        # tiles and tileCoords are part of the public API
        self.tiles = {}
        self.tileCoords = []

        stop = None
        if debug:
            stop = datetime.now()
            print(f'preprocess data took {stop -start}')
            print(
                f'index: maxZoom: {options.indexMaxZoom}, maxPoints: {options.indexMaxPoints}')
            start = datetime.now()
            self.stats = {}
            self.total = 0

        # wraps features (ie extreme west and extreme east)
        features = wrap(features, options)

        # start slicing from the top tile down
        if len(features) > 0:
            self.splitTile(features, 0, 0, 0)

        if debug:
            if len(features) > 0:
                print(
                    f'features: {self.tiles[0].numFeatures}, points: {self.tiles[0].numPoints}')
            stop = datetime.now()
            print(f'generate tiles took {stop -start}')
            print('tiles generated:', self.total, self.stats)

    # splits features from a parent tile to sub-tiles.
    # z, x, and y are the coordinates of the parent tile
    # cz, cx, and cy are the coordinates of the target tile
    #
    # If no target tile is specified, splitting stops when we reach the maximum
    # zoom or the number of points is low as specified in the options.

    def splitTile(self, features, z, x, y, cz, cx, cy):
        stack = [features, z, x, y]
        options = self.options
        debug = options.debug
        start = None
        stop = None
        # avoid recursion by using a processing queue
        while len(stack) > 0:
            y = stack.pop()
            x = stack.pop()
            z = stack.pop()
            features = stack.pop()

            z2 = 1 << z
            id_ = toID(z, x, y)
            tile = self.tiles[id_]

            if tile is None:
                if debug > 1:
                    print('creation')
                    start = datetime.now()

                tile = self.tiles[id_] = createTile(features, z, x, y, options)
                self.tileCoords.push({z, x, y})

                if debug:
                    if debug > 1:
                        print('tile z%d-%d-%d (features: %d, points: %d, simplified: %d)'.format(
                            z, x, y, tile.numFeatures, tile.numPoints, tile.numSimplified))
                        stop = datetime.now()
                        print(f'creation took {stop-start}')
                    key = f'z{z}'
                    self.stats[key] = (self.stats[key] or 0) + 1
                    self.total += 1

            # save reference to original geometry in tile so that we can drill down later if we stop now
            tile.source = features

            # if it's the first-pass tiling
            if cz is None:
                # stop tiling if we reached max zoom, or if the tile is too simple
                if z == options.indexMaxZoom or tile.numPoints <= options.indexMaxPoints:
                    continue  # if a drilldown to a specific tile
            elif z == options.maxZoom or z == cz:
                # stop tiling if we reached base zoom or our target tile zoom
                continue
            elif cz is not None:
                # stop tiling if it's not an ancestor of the target tile
                zoomSteps = cz - z
                if x != cx >> zoomSteps or y != cy >> zoomSteps:
                    continue

            # if we slice further down, no need to keep source geometry
            tile.source = None

            if len(features) == 0:
                continue

            if debug > 1:
                print('clipping')
                start = datetime.now()

            # values we'll use for clipping
            k1 = 0.5 * options.buffer / options.extent
            k2 = 0.5 - k1
            k3 = 0.5 + k1
            k4 = 1 + k1

            tl = None
            bl = None
            tr = None
            br = None

            left = clip(features, z2, x - k1, x + k3, 0,
                        tile.minX, tile.maxX, options)
            right = clip(features, z2, x + k2, x + k4, 0,
                         tile.minX, tile.maxX, options)
            features = None

            if left is not None:
                tl = clip(left, z2, y - k1, y + k3, 1,
                          tile.minY, tile.maxY, options)
                bl = clip(left, z2, y + k2, y + k4, 1,
                          tile.minY, tile.maxY, options)
                left = None

            if right is not None:
                tr = clip(right, z2, y - k1, y + k3, 1,
                          tile.minY, tile.maxY, options)
                br = clip(right, z2, y + k2, y + k4, 1,
                          tile.minY, tile.maxY, options)
                right = None

            if debug > 1:
                stop = datetime.now()
                print(f'clipping took {stop-start}')

            stack.push(tl or [], z + 1, x * 2,     y * 2)
            stack.push(bl or [], z + 1, x * 2,     y * 2 + 1)
            stack.push(tr or [], z + 1, x * 2 + 1, y * 2)
            stack.push(br or [], z + 1, x * 2 + 1, y * 2 + 1)

    def getTile(self, z, x, y):
        z = + z
        x = +x
        y = + y

        options = self.options
        extent, debug = options

        if z < 0 or z > 24:
            return None

        z2 = 1 << z
        x = (x + z2) & (z2 - 1)  # wrap tile x coordinate

        id_ = toID(z, x, y)
        if self.tiles[id_] is not None:
            return transform(self.tiles[id_], extent)

        if debug > 1:
            print('drilling down to z%d-%d-%d'.format(z, x, y))

        z0 = z
        x0 = x
        y0 = y
        parent = None

        while parent is None and z0 > 0:
            z0 -= 1
            x0 = x0 >> 1
            y0 = y0 >> 1
            parent = self.tiles[toID(z0, x0, y0)]

        if parent is None or parent.source is None:
            return None

        # if we found a parent tile containing the original geometry, we can drill down from it
        start = None
        if debug > 1:
            print('found parent tile z%d-%d-%d'.format(z0, x0, y0))
            print('drilling down')
            start = datetime.now()

        self.splitTile(parent.source, z0, x0, y0, z, x, y)

        if debug > 1:
            stop = datetime.now()
            print(f'drilling down took {stop -start}')

        return transform(self.tiles[id_], extent) if self.tiles[id_] is not None else None


def toID(z, x, y):
    return (((1 << z) * y + x) * 32) + z


def extend(dest, src):
    for i in src:
        dest[i] = src[i]
    return dest


def geojsonvt(data, options):
    return GeoJSONVT(data, options)
