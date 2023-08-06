import logging
import filter
LOG = logging.getLogger("keep")


class Keep(filter.Filter):
    """Keeps only the indicated, comma-delimited list of fields"""
    def __init__(self, spec):
        super(filter.Filter, self).__init__()
        self.keeps = spec.split(',')

    def filter_events(self, events):
        for e in events:
            for k in e.keys():
                if not k in self.keeps:
                    e.pop(k)
            yield e