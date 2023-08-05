from csp import Channel, alts

import csp.impl.operations as op


def main():
    # chan = Channel()
    # out = op.map_from(lambda x: x * 2, chan)

    # def counter(n):
    #     i = n
    #     while True:
    #         yield put(chan, i)
    #         i += 1

    # go(counter(0))

    # while True:
    #     value = yield take(out)
    #     if value > 20:
    #         yield stop(value)
    #     print value

    i = Channel()
    def m(x):
        y = x * 2
        print "\t\t\t", x, "=>", y
        return y
    o = op.map_from(m, i)

    for x in range(10):
        result = yield alts([[i, x], o])
        if result.value is None: # write
            print x
        else:
            print "\t", result.value
        # print result
