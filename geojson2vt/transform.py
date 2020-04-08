import math
# Transforms the coordinates of each feature in the given tile from
# mercator-projected space into (extent x extent) tile space.


def transformTile(tile, extent):
    if tile.transformed:
        return tile

    z2 = 1 << tile.z
    tx = tile.x
    ty = tile.y

    for feature in tile.features:
        geom = feature.geometry
        type_ = feature.type

        feature.geometry = []

        if type_ == 1:
            for j in range(len(geom), step=2):
                feature.geometry.append(transformPoint(
                    geom[j], geom[j + 1], extent, z2, tx, ty))
        else:
            for j in range(len(geom)):
                ring = []
                for k in range(len(geom[j]), step=2):
                    ring.append(transformPoint(
                        geom[j][k], geom[j][k + 1], extent, z2, tx, ty))
                feature.geometry.append(ring)

    tile.transformed = True
    return tile


def transformPoint(x, y, extent, z2, tx, ty):
    return [
        math.round(extent * (x * z2 - tx)),
        math.round(extent * (y * z2 - ty))
    ]
