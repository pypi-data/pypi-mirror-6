import g11pyutils as utils

class CSVOut(object):
    def __init__(self, spec=None):
        self.fo = utils.fout(spec)

    def process(self, events):
        keys = None
        for e in events:
            if not keys:
                keys = e.keys()
                self.fo.write(','.join(keys))
                self.fo.write('\n')
            self.fo.write(','.join([str(e.get(k, '')) for k in keys]))
            self.fo.write('\n')
        self.fo.flush()