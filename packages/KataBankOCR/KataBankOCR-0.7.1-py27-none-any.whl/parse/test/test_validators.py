"test the validators module"

import pytest

from parse.validators import Validate
from fixture_methods import ArbitraryValues

_name = 'Arbitrary Thing'

class TestType():
    "exercise the Validate.type method"

    matched_type_value_pairs = ((basestring, 'foo'), (list, []), (tuple, ()), (int, 1))
    @pytest.mark.parametrize("expected_type, value", matched_type_value_pairs)
    def test_with_valid_type(self, expected_type, value):
        "confirm passes silently on value of valid type"
        assert None == Validate.type(expected_type, value, _name)

    mismatched_type_value_pairs = ((int, 'A',), (tuple, [],), (basestring, (1,)))
    @pytest.mark.parametrize("expected_type, value", mismatched_type_value_pairs)
    def test_with_invalid_type(self, expected_type, value):
        "confirm raises with expected message on invalid type"
        message = '%s "%s" of unexpected type. Expected:%s. Found:%s.'
        message = message % (_name, value, expected_type, str(type(value)))
        arguments = (expected_type, value, _name)
        e = pytest.raises(TypeError, Validate.type, *arguments)
        assert message == e.value.message

class TestLength():
    "exercise the Validate.length method"

    matched_length_value_pairs = ((0, ''), (0, []), (0, ()), (1, 'A'),
                                  (2, 'ab'), (2, [1, 2]), (3, (1, 2, 3)))
    @pytest.mark.parametrize("length, value", matched_length_value_pairs)
    def test_with_valid_length(self, length, value):
        "confirm passes silently on value of valid length"
        assert None == Validate.length(length, value, _name)

    mismatched_length_value_pairs = ((2, 'A',), (1, []), (0, (1,)))
    @pytest.mark.parametrize("expected_length, value", mismatched_length_value_pairs)
    def test_with_invalid_length(self, expected_length, value):
        "confirm raises correctly on invalid length"
        message = '%s "%s" of unexpected length. Expected:%d. Found:%d.'
        message = message % (_name, value, expected_length, len(value))
        arguments = (expected_length, value, _name)
        e = pytest.raises(ValueError, Validate.length, *arguments)
        assert message == e.value.message

class TestComposition():
    "exercise the Validate.composition method"

    matched_components_value_pairs = ((['a', 'b', 'c'], 'baabccab'),
                                      (['ab', 'XY', 'zz'], ('XY', 'ab', 'ab')),
                                      ((10, 20, 30), [20, 10, 10]),
                                      ([0, 1, 2, 3], (1, 2, 2, 1, 0)),
                                      ([1, 2, 3], ()),)
    @pytest.mark.parametrize("allowed_components, value", matched_components_value_pairs)
    def test_with_valid_composition(self, allowed_components, value):
        "confirm passes silently on value with allowed components"
        assert None == Validate.composition(allowed_components, value, _name)

    mismatched_components_value_index_triads = ((['a', 'b', 'c'], 'abcd', 3),
                                                ((10, 20, 30), [1, 2], 0),
                                                ([0, 1, 2, 3], (2, 4, 6), 1),
                                                (['ab', 'bc', 'de'], 'abbcde', 0),)
    @pytest.mark.parametrize("allowed_components, value, bad_index",
                             mismatched_components_value_index_triads)
    def test_with_invalid_composition(self, allowed_components, value, bad_index):
        "confirm raises correctly on value containing an unexpected element"
        unexpected_element = value[bad_index]
        message = '%s "%s" contains unexpected element "%s" at index %d'
        message = message % (_name, value, unexpected_element, bad_index)
        arguments = (allowed_components, value, _name)
        e = pytest.raises(TypeError, Validate.composition, *arguments)
        assert message == e.value.message
