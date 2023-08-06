from collections import deque

# Python 2 compatibility
try:
    xrange
except NameError:
    xrange = range

def window(seq, n=2):
    it = iter(seq)
    win = deque((next(it, None) for _ in xrange(n)), maxlen=n)
    yield win
    append = win.append
    for e in it:
        append(e)
        yield win
