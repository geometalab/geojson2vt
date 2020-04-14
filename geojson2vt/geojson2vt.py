import logging
from datetime import datetime

from geojson2vt.convert import convert
from geojson2vt.clip import clip
from geojson2vt.wrap import wrap
from geojson2vt.transform import transform_tile
from geojson2vt.tile import create_tile


def get_default_options():
    return {
        "maxZoom": 14,            # max zoom to preserve detail on
        "indexMaxZoom": 5,        # max zoom in the tile index
        "indexMaxPoints": 100000,  # max number of points per tile in the tile index
        # simplification tolerance (higher means simpler)
        "tolerance": 3,
        "extent": 4096,           # tile extent
        "buffer": 64,             # tile buffer on each side
        "lineMetrics": False,     # whether to calculate line metrics
        "promoteId": None,        # name of a feature property to be promoted to feature.id
        "generateId": False,      # whether to generate feature ids. Cannot be used with promoteId
    }


class GeoJsonVt:
    def __init__(self, data, options, log_level=logging.INFO):
        logging.basicConfig(
            level=log_level, format='%(asctime)s %(levelname)s %(message)s')
        options = self.options = extend(get_default_options(), options)

        logging.debug('preprocess data start')

        if options.get('maxZoom') < 0 or options.get('maxZoom') > 24:
            raise Exception('maxZoom should be in the 0-24 range')
        if options.get('promoteId', None) is not None and options.get('generateId', False):
            raise Exception(
                'promoteId and generateId cannot be used together.')

        # projects and adds simplification info
        features = convert(data, options)

        # tiles and tile_coords are part of the public API
        self.tiles = {}
        self.tile_coords = []

        logging.debug(f'preprocess data end')
        logging.debug(
            f'index: maxZoom: {options.get("indexMaxZoom")}, maxPoints: {options.get("indexMaxPoints")}')
        self.stats = {}
        self.total = 0

        # wraps features (ie extreme west and extreme east)
        features = wrap(features, options)

        # start slicing from the top tile down
        if len(features) > 0:
            self.split_tile(features, 0, 0, 0)

        if len(features) > 0:
            logging.debug(
                f'features: {self.tiles[0].get("numFeatures")}, points: {self.tiles[0].get("numPoints")}')
            stop = datetime.now()
        logging.debug(f'generate tiles end')
        logging.debug('tiles generated:', self.total, self.stats)

    # splits features from a parent tile to sub-tiles.
    # z, x, and y are the coordinates of the parent tile
    # cz, cx, and cy are the coordinates of the target tile
    #
    # If no target tile is specified, splitting stops when we reach the maximum
    # zoom or the number of points is low as specified in the options.

    def split_tile(self, features, z, x, y, cz=None, cx=None, cy=None):
        stack = [features, z, x, y]
        options = self.options
        # avoid recursion by using a processing queue
        while len(stack) > 0:
            y = stack.pop()
            x = stack.pop()
            z = stack.pop()
            features = stack.pop()

            z2 = 1 << z
            id_ = to_Id(z, x, y)
            tile = self.tiles.get(id_, None)

            if tile is None:
                logging.debug('creation start')

                self.tiles[id_] = create_tile(features, z, x, y, options)
                tile = self.tiles[id_]
                self.tile_coords.append({'z': z, 'x': x, 'y': y})

                logging.debug(
                    f'tile z{z}-{x}-{y} (features: {tile.get("numFeatures")}, points: {tile.get("numPoints")}, simplified: {tile.get("numSimplified")})')
                logging.debug(f'creation end')
                key = f'z{z}'
                self.stats[key] = self.stats.get(key, 0) + 1
                self.total += 1

            # save reference to original geometry in tile so that we can drill down later if we stop now
            tile['source'] = features

            # if it's the first-pass tiling
            if cz is None:
                # stop tiling if we reached max zoom, or if the tile is too simple
                if z == options.get('indexMaxZoom') or tile.get('numPoints') <= options.get('indexMaxPoints'):
                    continue  # if a drilldown to a specific tile
            elif z == options.get('maxZoom') or z == cz:
                # stop tiling if we reached base zoom or our target tile zoom
                continue
            elif cz is not None:
                # stop tiling if it's not an ancestor of the target tile
                zoomSteps = cz - z
                if x != (cx >> zoomSteps) or y != (cy >> zoomSteps):
                    continue

            # if we slice further down, no need to keep source geometry
            tile['source'] = None

            if not features or len(features) == 0:
                continue

            logging.debug('clipping start')

            # values we'll use for clipping
            k1 = 0.5 * options.get('buffer') / options.get('extent')
            k2 = 0.5 - k1
            k3 = 0.5 + k1
            k4 = 1 + k1

            tl = None
            bl = None
            tr = None
            br = None

            left = clip(features, z2, x - k1, x + k3, 0,
                        tile['minX'], tile['maxX'], options)
            right = clip(features, z2, x + k2, x + k4, 0,
                         tile['minX'], tile['maxX'], options)
            features = None

            if left is not None:
                tl = clip(left, z2, y - k1, y + k3, 1,
                          tile['minY'], tile['maxY'], options)
                bl = clip(left, z2, y + k2, y + k4, 1,
                          tile['minY'], tile['maxY'], options)
                left = None

            if right is not None:
                tr = clip(right, z2, y - k1, y + k3, 1,
                          tile['minY'], tile['maxY'], options)
                br = clip(right, z2, y + k2, y + k4, 1,
                          tile['minY'], tile['maxY'], options)
                right = None

            logging.debug(f'clipping took end')

            #stack.push(tl or [], z + 1, x * 2,     y * 2)
            stack.append(tl if tl is not None else [])
            stack.append(z + 1)
            stack.append(x * 2)
            stack.append(y * 2)

            #stack.push(bl or [], z + 1, x * 2,     y * 2 + 1)
            stack.append(bl if bl is not None else [])
            stack.append(z + 1)
            stack.append(x * 2)
            stack.append(y * 2 + 1)

            #stack.push(tr or [], z + 1, x * 2 + 1, y * 2)
            stack.append(tr if tr is not None else [])
            stack.append(z + 1)
            stack.append(x * 2 + 1)
            stack.append(y * 2)

            #stack.push(br or [], z + 1, x * 2 + 1, y * 2 + 1)
            stack.append(br if br is not None else [])
            stack.append(z + 1)
            stack.append(x * 2 + 1)
            stack.append(y * 2 + 1)

    def get_tile(self, z, x, y):
        z = int(z)
        x = int(x)
        y = int(y)

        options = self.options
        extent = options.get('extent')

        if z < 0 or z > 24:
            return None

        z2 = 1 << z
        x = (x + z2) & (z2 - 1)  # wrap tile x coordinate

        id_ = to_Id(z, x, y)
        current_tile = self.tiles.get(id_, None)
        if current_tile is not None:
            return transform_tile(self.tiles[id_], extent)

        logging.debug(f'drilling down to z{z}-{x}-{y}')

        z0 = z
        x0 = x
        y0 = y
        parent = None

        while parent is None and z0 > 0:
            z0 -= 1
            x0 = x0 >> 1
            y0 = y0 >> 1
            parent = self.tiles.get(to_Id(z0, x0, y0), None)

        if parent is None or parent.get('source', None) is None:
            return None

        # if we found a parent tile containing the original geometry, we can drill down from it
        logging.debug(f'found parent tile z{z0}-{x0}-{y0}')
        logging.debug('drilling down start')

        self.split_tile(parent.get('source'), z0, x0, y0, z, x, y)

        logging.debug(f'drilling down end')

        transformed = transform_tile(self.tiles[id_], extent) if self.tiles.get(
            id_, None) is not None else None
        return transformed


def to_Id(z, x, y):
    id_ = (((1 << z) * y + x) * 32) + z
    return id_


def extend(dest, src):
    for key, _ in src.items():
        dest[key] = src[key]
    return dest


def geojson2vt(data, options, log_level=logging.INFO):
    return GeoJsonVt(data, options, log_level)
