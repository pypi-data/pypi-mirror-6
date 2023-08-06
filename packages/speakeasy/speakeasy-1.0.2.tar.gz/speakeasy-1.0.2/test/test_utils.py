from nose.tools import eq_
from speakeasy.utils import percentile

def test_percentile_empty():
    eq_(percentile([], 0.5), None)

def test_percentile_single():
    eq_(percentile([0], 0.9), 0)
    eq_(percentile([1], 0.5), 1)
    eq_(percentile([1], 0.0), 0)

def test_percentile_multiple():
    eq_(percentile(range(11), 0.0), 0)
    eq_(percentile(range(11), 0.1), 1)
    eq_(percentile(range(11), 0.5), 5)
    eq_(percentile(range(11), 0.9), 9)
