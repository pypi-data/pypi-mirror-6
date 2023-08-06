import logging
import g11pyutils as utils
LOG = logging.getLogger("bucket")


class Bucket(object):
    """Converts individual events to lists of events.  If events are already coming in as buckets,
    then re-buckets them.  User with negative arguments to distribute into N buckets (requires
    getting whole list into memory).  Use 0 to unbucket"""
    def __init__(self, size = 0):
        self.size = int(size)

    def filter(self, events):
        bucket = []
        for e in events:
            if isinstance(e, dict):  # Single event, append
                bucket.append(e)
            else:
                bucket += list(e)  # List, add all to bucket
            if self.size == 0:  # Unbucket
                for b in bucket:
                    yield b
                bucket = []
            while 1 <= self.size <= len(bucket):  # Re-bucket (positive)
                b = bucket[0:self.size]
                bucket = bucket[self.size:]
                yield b
        if self.size >= 1 and len(bucket):  # Re-bucket (positive)
            yield bucket   # Leftover
        elif self.size < 0: # Must be re-bucketing into N
            n_buckets = -self.size
            b_size = len(bucket) / n_buckets  # Num events/bucket (if no extra)
            extra = len(bucket) % n_buckets  # Num of buckets with an extra item
            LOG.info("Splitting %s items into %s buckets (%s items per bucket)", len(bucket), n_buckets, b_size)
            n = 0
            while n < len(bucket):
                sz = b_size
                if extra > 0:
                    sz += 1
                    extra -= 1
                yield bucket[n:n+sz] if n+sz < len(bucket) else bucket[n:]
                n += sz







