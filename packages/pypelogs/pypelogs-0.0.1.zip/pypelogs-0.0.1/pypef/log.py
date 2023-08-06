import g11pyutils as utils

class Log(object):
    """Logs events as they pass through"""
    def __init__(self, spec = None):
        self.fo = utils.fout(spec)

    def filter(self, events):
        for e in events:
            self.fo.write(repr(e))
            self.fo.write('\n')
            self.fo.flush()
            yield e