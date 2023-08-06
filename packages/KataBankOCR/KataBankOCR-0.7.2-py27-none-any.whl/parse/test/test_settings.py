"test the settings module"

import pytest
from types import FunctionType

from parse import settings

expected_setting_types = (
    ('lines_per_entry', int),
    ('figures_per_entry', int),
    ('strokes_per_substring', int),
    ('strokes_per_figure', int),
    ('strokes_per_line', int),
    ('some_known_valid_accounts', tuple),
    ('some_known_invalid_accounts', tuple),
    ('valid_strokes', set),
    ('valid_numerals', set),
    ('figures', dict),
    ('illegible_numeral', str),
    ('ambiguous_status', str),
    ('checksum', FunctionType),
    )

class TestDefinition:
    "confirm expected settings defined and of correct type"

    @pytest.fixture(params=expected_setting_types)
    def setting_name_and_type(self, request):
        "return (setting_name, setting_type)"
        return request.param

    def test_setting_defined(self, setting_name_and_type):
        "confirm setting got defined"
        setting_name = setting_name_and_type[0]
        assert setting_name in settings.__dict__

    def test_setting_of_correct_type(self, setting_name_and_type):
        "confirm setting has expected type"
        setting_name, setting_type = setting_name_and_type
        value = settings.__dict__[setting_name]
        assert isinstance(value, setting_type)

    def test_total_setting_count_matches_expectations(self):
        "confirm settings contains exactly as many entries as expected"
        attributes_of_settings_module = settings.__dict__.keys()
        builtins_of_settings_module = filter(lambda k: '__' in k, attributes_of_settings_module)
        found_settings = set(attributes_of_settings_module) - set(builtins_of_settings_module)
        assert len(expected_setting_types) == len(found_settings)

class TestUniqueness:
    "confirm no duplicate Figures, Numerals, or Strokes"

    @pytest.mark.parametrize('collection', (settings.figures.keys(), settings.valid_numerals,
                                            settings.figures.values(), settings.valid_strokes,))
    def test_uniqueness_of_collection(self, collection):
        "confirm no duplicates"
        assert len(collection) == len(set(collection))

class TestRepresentation:
    "confirm a Figure exists that represents each Numeral"

    def test_numeral_representation(self):
        represented_numerals = settings.figures.values()
        assert set(represented_numerals) == set(settings.valid_numerals)

class TestStringConstruction:
    "confirm length and composition of strings"

    class TestFigureConstruction:
        "confirm length and composition of all Figures"

        @pytest.fixture(params=settings.figures.keys())
        def figure(self, request):
            "return a Figure that represents a Numeral"
            return request.param

        def test_length_of_figure(self, figure):
            "confirm Figure contains the correct number of Strokes"
            assert len(figure) == settings.strokes_per_figure

        def test_figure_composition(self, figure):
            "confirm Figure composed only of valid Strokes"
            assert set(figure).issubset(settings.valid_strokes)

    class TestAccountConstruction:
        "confirm length and composition of all Accounts"

        some_valid = settings.some_known_valid_accounts
        some_invalid = settings.some_known_invalid_accounts
        @pytest.fixture(params=list(some_valid + some_invalid))
        def account(self, request):
            "return an Account"
            return request.param

        def test_length_of_account(self, account):
            "confirm Account of correct length"
            assert len(account) == settings.figures_per_entry

        def test_account_composition(self, account):
            "confirm Account composed only of valid Numerals"
            assert set(account).issubset(settings.valid_numerals)

    class TestNumeralConstruction:
        "confirm length and composition of valid Numerals"

        @pytest.fixture(params=settings.figures.values())
        def numeral(self, request):
            "return a Numeral represented by settings.figures"
            return request.param

        def test_length_of_numeral(self, numeral):
            "confirm Numeral has length of one"
            assert len(numeral) == 1

        def test_numeral_validity(self, numeral):
            "confirm numeral validity"
            assert numeral in settings.valid_numerals

    class TestStrokeConstruction:
        "confirm length of valid Strokes"

        @pytest.mark.parametrize('stroke', settings.valid_strokes)
        def test_length_of_stroke(self, stroke):
            "confirm Stroke exactly one character long"
            assert len(stroke) == 1

    class TestIllegibleNumeralConstruction:
        "confirm length and uniqueness of illegible_numeral"

        def test_length_of_illegible_numeral(self):
            "confirm llegible_numeral exactly one character long"
            assert len(settings.illegible_numeral) == 1

        def test_illegible_numeral_distinct_from_valid_numerals(self):
            "confirm llegible_numeral not in valid_numerals"
            assert settings.illegible_numeral not in settings.valid_numerals

class TestChecksumFunction:
    "confirm checksum meets expectations"

    class TestArgumentCount:
        "confirm checksum accepts exactly one argument"

        def test_with_no_argument(self):
            "confirm checksum requires more than zero arguments"
            pytest.raises(TypeError, settings.checksum)

        @pytest.mark.parametrize('arg_count', range(2, 20))
        def test_with_multiple_arguments(self, arg_count):
            "confirm checksum raises error on multiple arguments"
            pytest.raises(TypeError, settings.checksum, *range(arg_count))

    class TestFunctionality:
        "confirm checksum correctly categorizes known Accounts"

        @pytest.mark.parametrize('valid_account', settings.some_known_valid_accounts)
        def test_with_known_good_account(self, valid_account):
            "confirm checksum reports a known good Account as valid"
            assert settings.checksum(valid_account)

        @pytest.mark.parametrize('invalid_account', settings.some_known_invalid_accounts)
        def test_with_known_bad_account(self, invalid_account):
            "confirm checksum reports a known bad Account as invalid"
            assert not settings.checksum(invalid_account)

class TestIntegerValues:
    "confirm integer settings have reasonable values"

    @pytest.mark.parametrize('setting_name, arbitrary_maximum', (
            ('lines_per_entry', 50),
            ('figures_per_entry', 50),
            ('strokes_per_substring', 50),
            ('strokes_per_figure', 250),
            ('strokes_per_line', 1000),
            ))
    def test_integer_setting_has_reasonable_value(self, setting_name, arbitrary_maximum):
        "confirm value does not exceed arbitrary maximum"
        value = settings.__dict__[setting_name]
        assert 0 <= value <= arbitrary_maximum
