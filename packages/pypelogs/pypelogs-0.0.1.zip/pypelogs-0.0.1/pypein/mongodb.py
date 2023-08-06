import g11pyutils as utils
import logging
from pypeout import MongoDB
from bson.son import SON


LOG = logging.getLogger("MongoDB")

class MongoDBGeo(MongoDB):
    def __init__(self, spec, host='127.0.0.1', port=27017, buffer=1000):
        super(MongoDBGeo, self).__init__(spec, host, port, buffer)
        opts = utils.to_dict(spec.split(",", 1)[1])
        self.coords = [float(c) for c in opts.get("coords").split(':')]

    def __iter__(self):
        if len(self.coords) == 2: # Geonear
            for r in self.db().command(SON([('geoNear', self.coll), ('near', [self.coords[1], self.coords[0]]), ('spherical', True)]))['results']:
                doc = r['obj']
                doc['dis'] = r['dis']
                doc['_id'] = repr(doc['_id'])
                yield doc
        else:
            if len(self.coords) == 4:  # Bounding box of lat1:lon1:lat2:lon2
                q = ""
            elif len(self.coords) == 3:  # geonear lat:lon:results
                q = {"loc": {"$within": {"$center": [[0, 0], 6]}}}
            for doc in self.collection().find(q):
                yield doc