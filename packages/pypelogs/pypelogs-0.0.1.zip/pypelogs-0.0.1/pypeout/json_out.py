import json
import g11pyutils as utils

class JSONOut(object):
    def __init__(self, spec=None):
        self.fo = utils.fout(spec)

    def process(self, pin):
        for e in pin:
            self.fo.write(json.dumps(e))
            self.fo.write("\n")
            self.fo.flush()