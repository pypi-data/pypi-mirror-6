import logging
import filter
import operator
LOG = logging.getLogger("sorts")


class Sort(filter.Filter):
    """Sorts on the indicated, comma-delimited list of fields"""
    def __init__(self, spec):
        super(filter.Filter, self).__init__()
        self.sort_keys = spec.split(',')

    def filter_events(self, events):
        l = list(events)
        s = l
        for k in reversed(self.sort_keys):
            s = sorted(s, key=operator.itemgetter(k))
        for e in s:
            yield e