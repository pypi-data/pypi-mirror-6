import nose.tools as n

from to_function import to_function

def test_to_function():
    fstr = to_function(str)
    n.assert_equal(fstr.__doc__, str.__doc__)
    n.assert_equal(fstr.__name__, str.__name__)
    n.assert_equal(fstr(), str())
    n.assert_is_instance(fstr, type(lambda:None))
