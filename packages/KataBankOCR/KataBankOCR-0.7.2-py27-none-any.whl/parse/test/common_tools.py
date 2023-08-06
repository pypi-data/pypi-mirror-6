"functions used by test modules to prepare values for testing"

import random

def bad_length_duplicator(value):
    "return values with bad lengths from one value with good length"
    return [_fit_to_length(value, length) for length in _invalid_lengths(value)]

def _invalid_lengths(value):
    "return list of ints 0 to (valid_length * 4) excluding valid_length"
    valid_length = len(value)
    maximum_bad_length = valid_length * 4  # an arbitrary multiplier
    lengths = range(maximum_bad_length + 1)
    return [L for L in lengths if L != valid_length]

def _fit_to_length(value, length):
    "return duplicated & abbreviated value such that len(value) == length"
    if len(value) == length:
        return value
    elif len(value) > length:
        return value[:length]
    # Still too short. Double it and recurse.
    return _fit_to_length(value + value, length)

def adulterate_iterable(target, new_element, index=None):
    "return string or list after replacing a [random] element"
    assert isinstance(target, (list, basestring))
    if index is None:
        index = random.randrange(0, len(target))
    if isinstance(target, basestring):
        return ''.join((target[:index], new_element, target[index + 1:]))
    elif isinstance(target, list):
        target[index] = new_element
        return target

def get_one_or_more(function, count=None):
    "return just one or a list of function's return values"
    if count is None:
        return function()
    return [function() for _ in range(count)]
