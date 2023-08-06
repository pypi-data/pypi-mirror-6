# encoding: utf-8

from attest import Tests
from xmlpumpkin.utils import cacheonceproperty


utils_unit = Tests()


@utils_unit.test
def cachedproperty():
    """Super simple cached property works?"""
    numbers = (1, 3, 4, 7, 11, 18)
    sum_numners = sum(numbers)

    class Cached(object):
        def __init__(self, init_numbers):
            self.nums = init_numbers
        @cacheonceproperty  # calculate only once!
        def summation(self):
            return sum(self.nums)

    c = Cached(numbers)
    assert c.summation == sum_numners

    # with data change
    new_numbers = (2, 4, 6, 10, 16, 26)
    sum_new_numbers = sum(new_numbers)
    assert sum_numners != sum_new_numbers

    c.nums = new_numbers
    assert c.summation == sum_numners

    # on other instance
    c2 = Cached(new_numbers)
    assert c2.summation == sum_new_numbers

@utils_unit.test
def fgetonly():
    """cacheonceproperty is only for getters?"""
    try:
        class HasSetter(object):
            def __init__(self):
                self._attr = 0
            def _attr_getter(self):
                return self._attr
            def _attr_setter(self, val):
                self._attr = val
            attr = cacheonceproperty(_attr_getter, _attr_setter)

    except ValueError:
        assert True
    except:
        assert False, 'unexpected exception for cacheonceproperty'
    else:
        assert False, 'cacheonceproperty receives fset'
