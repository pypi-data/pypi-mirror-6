import nose.tools as n

import jumble.lib

def test_accurate():
    observed = set(future.result() for future in jumble.lib.jumble(lambda x: x+3, range(20)))
    expected = set(range(3, 23))
    n.assert_set_equal(observed, expected)
