from liji.ext._liji import inspect
import ujson
import json
from datetime import datetime

COUNT = 100000
jsondata = open('../fixtures/reallybigone.json').read()


def with_liji():
    inspect(jsondata, ["events", "picture"])


def with_ujson():
    parsed = ujson.loads(jsondata)
    [ev.get('user', {}).get('picture', None) for ev in parsed['events']]


def with_json():
    parsed = json.loads(jsondata)
    [ev.get('user', {}).get('picture', None) for ev in parsed['events']]


test_funcs = [
    with_liji,
    with_ujson,
    # with_json,
]

for func in test_funcs:
    t0 = datetime.now()
    for i in xrange(COUNT):
        func()
    t = datetime.now() - t0
    print "%s - %s" % (func.__name__, t)
