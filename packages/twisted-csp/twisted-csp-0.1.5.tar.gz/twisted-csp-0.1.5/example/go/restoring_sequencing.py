# http://talks.golang.org/2012/concurrency.slide#30

from csp import Channel, put, take
from collections import namedtuple

Message = namedtuple("Message", ["str", "wait"])

for i in range(5):
    msg1 = yield take(chan)
    print msg1.str
    msg2 = yield take(chan)
    print msg2.str
    yield put(msg1.wait, True)
    yield put(msg2.wait, True)

wait_for_it = Channel()

yield put(c,)
