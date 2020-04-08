def createFeature(id_, type_, geom, tags):
    containes_slices = len(geom) > 0 and isinstance(geom[0], Slice)
    #geom = geom if containes_slices else [slice_ for slice_ in geom.geom]
    feature = {
        "id": None if id_ is None else id_,
        "type": type_,
        "geometry": geom,
        "tags": tags,
        "minX": float('inf'),
        "minY": float('inf'),
        "maxX": float('-inf'),
        "maxY": float('-inf')
    }

    if type_ == 'Point' or type_ == 'MultiPoint' or type_ == 'LineString':
        calcLineBBox(feature, geom)
    elif type_ == 'Polygon':
        # the outer ring(ie[0]) contains all inner rings
        calcLineBBox(feature, geom[0])
    elif type_ == 'MultiLineString':
        for line in geom:
            calcLineBBox(feature, line)
    elif type_ == 'MultiPolygon':
        for polygon in geom:
            # the outer ring(ie[0]) contains all inner rings
            calcLineBBox(feature, polygon[0])

    return feature


def calcLineBBox(feature, geom):
    for i in range(0, len(geom), 3):
        feature['minX'] = min(feature.get('minX'), geom[i])
        feature['minY'] = min(feature.get('minY'), geom[i + 1])
        feature['maxX'] = max(feature.get('maxX'), geom[i])
        feature['maxY'] = max(feature.get('maxY'), geom[i + 1])


class Slice(list):
    def __init__(self, *args):
        list.__init__(self, *args)
        self.start = 0.
        self.end = 0.
        self.size = 0.

# class Slice:
#     def __init__(self, geom):
#         self.geom = geom
#         self.start = 0.
#         self.end = 0.
#         self.size = 0.

#     def __getitem__(self, key):
#         return self.geom[key]

#     def __len__(self):
#         return len(self.geom)

#     def __iadd__(self, other):  # += operator
#         self.geom += other.geom
#         return self.geom

#     def append(self, item):
#         self.geom.append(item)

#     def __str__(self):
#         return str(self.geom)
