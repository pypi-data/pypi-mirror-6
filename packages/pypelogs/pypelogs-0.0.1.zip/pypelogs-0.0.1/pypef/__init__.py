from bucket import Bucket
from each import Each
from groupby import GroupBy
from head import Head
from keep import Keep
from log import Log
from set import Set
from sort import Sort
from split import Split

CLASSES = {
    'bucket' : Bucket,
    'each' : Each,
    'groupby' : GroupBy,
    'head' : Head,
    'keep' : Keep,
    'log' : Log,
    'set' : Set,
    'sort' : Sort,
    'split' : Split

}

def filter_for(s):
    spec_args = s.split(':', 1)
    clz = CLASSES.get(spec_args[0])
    if not clz:
        raise ValueError("No such filter type: %s", spec_args[0])
    return clz() if len(spec_args) == 1 else clz(spec_args[1])
