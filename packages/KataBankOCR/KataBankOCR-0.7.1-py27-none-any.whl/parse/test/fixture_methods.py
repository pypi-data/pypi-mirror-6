"methods that provide values for testing and an interface to constants"

import os
import copy
import random
import fileinput

from parse import settings
import parse

from common_tools import get_one_or_more, adulterate_iterable, bad_length_duplicator
import fixture_constants

class Numerals:
    "methods that provide Numerals for testing"

    @classmethod
    def get_random(cls, count=None):
        "return random valid Numeral[s]"
        getter = lambda: random.choice(cls.valid())
        return get_one_or_more(getter, count)

    @staticmethod
    def valid():
        "return ordered list of valid Numerals"
        return sorted(list(settings.valid_numerals))

    @classmethod
    def invalid(cls):
        "return list of arbitrary basestrings that includes no valid numerals"
        litmus = lambda value: value not in cls.valid()
        return set(filter(litmus, ArbitraryValues.single_character_basestrings()))

class Accounts:
    "methods that provide Accounts for testing"

    @staticmethod
    def get_random(count=None):
        "return random Account[s]"
        getter = lambda: ''.join(Numerals.get_random(settings.figures_per_entry))
        return get_one_or_more(getter, count)

    @staticmethod
    def of_example_accounts():
        "return Accounts from superpositions of example Accounts"
        return [t[1] for t in fixture_constants.example_accounts]

    @staticmethod
    def of_basic_input_file():
        "return Accounts from basic input file"
        return fixture_constants.BasicInputFile.accounts

    @staticmethod
    def of_flawed_accounts():
        "return [in]valid Accounts from Superpositions with flaws"
        return [t[3] for t in fixture_constants.flawed_accounts]

class Figures:
    "methods that provide Figures for testing"

    @staticmethod
    def get_random(count=None):
        "return random valid Figure[s]"
        getter = lambda: random.choice(settings.figures.keys())
        return get_one_or_more(getter, count)

    @staticmethod
    def from_numeral(numeral):
        "return the Figure that represents the given Numeral"
        for figure in settings.figures:
            if settings.figures[figure] == numeral:
                return figure

    @classmethod
    def from_account(cls, account):
        "return the Figures that represent the given Account"
        return map(cls.from_numeral, list(account))

    @classmethod
    def valid(cls):
        "return ordered list of figures representing Numerals 0-9"
        return map(cls.from_numeral, Numerals.valid())

    @staticmethod
    def flawed():
        "return list of flawed Figures from fixture_constants"
        return [t[0] for t in fixture_constants.flawed_figures]

class Strokes:
    "methods that provide Strokes for testing"

    @classmethod
    def get_random(cls, count=None):
        "return random valid Stroke[s]"
        getter = lambda: random.choice(cls.valid())
        return get_one_or_more(getter, count)

    @staticmethod
    def valid():
        "return ordered list of valid Strokes"
        return sorted(list(settings.valid_strokes))

    @classmethod
    def invalid(cls):
        "return list of arbitrary single-char basestrings with 0 valid strokes"
        litmus = lambda value: value not in cls.valid()
        return filter(litmus, ArbitraryValues.single_character_basestrings())

class Lines:
    "methods that provide Lines for testing"

    @staticmethod
    def get_random(count=None):
        "return random Lines[s] composed of Strokes"
        return ''.join(Strokes.get_random(settings.strokes_per_line))

    @staticmethod
    def of_basic_input_file():
        "return Lines from basic input file"
        file = fileinput.input(Paths.basic_input_file())
        return [line.rstrip('\n') for line in file]

    @staticmethod
    def of_invalid_types():
        "return arbitrary values that do not include any basestrings"
        return ArbitraryValues.non_basestrings()

    @classmethod
    def of_invalid_lengths(cls):
        "return Lines of invalid length"
        return bad_length_duplicator(cls.get_random())

    @classmethod
    def with_invalid_strokes(cls):
        "return Lines that each include an invalid stroke"
        return map(cls._by_invalid_stroke, Strokes.invalid())

    @classmethod
    def _by_invalid_stroke(cls, invalid_stroke):
        "return a Line that includes an invalid stroke"
        return adulterate_iterable(cls.get_random(), invalid_stroke)

class Entries:
    "methods that provide Entries for testing"

    @classmethod
    def get_random(cls, count=None):
        "return one or more random Entries"
        getter = lambda: cls.from_account(Accounts.get_random())
        return get_one_or_more(getter, count)

    @classmethod
    def from_account(cls, account):
        "return the Entry (list of Lines) that represents the given Account"
        figures = Figures.from_account(account)
        return cls.from_figures(figures)

    @classmethod
    def from_figures(cls, figures):
        "return the Entry (list of Lines) that contains the given Figures"
        line_indexes = range(settings.lines_per_entry)
        return [cls._line_from_figures(line_index, figures) for line_index in line_indexes]

    @staticmethod
    def _line_from_figures(line_index, figures):
        "return a Line composed of Figures Substrings"
        first_figure_stroke = line_index * settings.strokes_per_substring
        last_figure_stroke = first_figure_stroke + settings.strokes_per_substring
        slice_indexes = (first_figure_stroke, last_figure_stroke)
        figure_substrings = [figure[slice(*slice_indexes)] for figure in figures]
        line = ''.join(figure_substrings)
        return line

    @classmethod
    def of_basic_input_file(cls):
        "return Entries from basic input file"
        return map(cls.from_account, Accounts.of_basic_input_file())

class Superpositions:
    "methods that provide Superpositions for testing"

    @classmethod
    def from_numeral(cls, numeral):
        "return Superposition of Figure representing Numeral"
        index = Numerals.valid().index(numeral)
        superposition = cls.of_valid_figures()[index]
        return superposition

    @classmethod
    def from_account(cls, account):
        "return list of Superpositions from Figures in Account's Numerals"
        return map(cls.from_numeral, account)

    @staticmethod
    def of_valid_figures():
        "return list of Superpositions for all un-flawed Figures"
        return copy.deepcopy(fixture_constants.valid_figure_superpositions)

    @staticmethod
    def of_flawed_figures():
        "return Superpositions of flawed figures"
        return [t[1] for t in fixture_constants.flawed_figures]

    @classmethod
    def of_example_accounts(cls):
        "return Superpositions made from example accounts"
        accounts = [t[0] for t in fixture_constants.example_accounts]
        return map(cls.from_account, accounts)

    @classmethod
    def of_flawed_accounts(cls):
        "return Superpositions of Accounts including flawed figures"
        count = len(fixture_constants.flawed_accounts)
        return [cls._by_flawed_figure_index(i) for i in range(count)]

    @classmethod
    def _by_flawed_figure_index(cls, flawed_figure_index):
        "return Superpositions of an Account including a flawed figure"
        flawed_account = fixture_constants.flawed_accounts[flawed_figure_index]
        account_prefix, flawed_figure_index, account_suffix, _, _ = flawed_account
        flawed_figure_superposition = cls.of_flawed_figures()[flawed_figure_index]
        prefix_superpositions = cls.from_account(account_prefix)
        suffix_superpositions = cls.from_account(account_suffix)
        return prefix_superpositions + [flawed_figure_superposition] + suffix_superpositions

class Results:
    "methods that provide Results for testing"

    @staticmethod
    def of_example_accounts():
        "return Results from example accounts"
        return [t[2] for t in fixture_constants.example_accounts]

    @staticmethod
    def of_basic_input_file():
        "return Results from the basic input file"
        return fixture_constants.BasicInputFile.results

    @staticmethod
    def of_advanced_input_file():
        "return Results from the advanced input file"
        return fixture_constants.AdvancedInputFile.results

    @staticmethod
    def of_flawed_accounts():
        "return Results of Accounts including flawed figures"
        return [t[4] for t in fixture_constants.flawed_accounts]

class ArbitraryValues:
    "methods that provide arbitrary values for testing"

    _all = [0, 1, -10, -999999999, 123456789, 3.14159, -.00000000001,
            False, True, [], (), {}, '', None, object, int, list, dict, bool,
            [1, 2, 3], {1: 2}, {0}, (1, 2, 3), {1: 'a', 2: 'b'},
            'abc', '|', '-', '\r', 'foo', '1', '0', 'c', '=', '\t', '\r',
            u'abc', u'|', u'-', u'\r', u'foo', u'1', u'0', u'c', u'=', u'\t', u'\r',
            ]

    @classmethod
    def iterables(cls):
        "return a list of arbitrary values over which one can iterate"
        return filter(cls._iterable, cls._all)

    @classmethod
    def non_iterables(cls):
        "return a list of arbitrary values over which one cannot iterate"
        not_iterable = lambda value: not cls._iterable(value)
        return filter(not_iterable, cls._all)

    @staticmethod
    def _iterable(value):
        "return True if value iterable"
        try:
            iterator = iter(value)
            return True
        except TypeError:
            return False

    @classmethod
    def single_character_basestrings(cls):
        "return list of arbitrary single character basestrings"
        litmus = lambda value: len(value) == 1
        return filter(litmus, cls.basestrings())

    @classmethod
    def basestrings(cls):
        "return list of arbitrary basestrings"
        litmus = lambda value: isinstance(value, basestring)
        return filter(litmus, cls._all)

    @classmethod
    def non_basestrings(cls):
        "return set of arbitrary values that includes no basestrings"
        litmus = lambda value: not isinstance(value, basestring)
        return filter(litmus, cls._all)

    @classmethod
    def of_different_type(cls, value_or_type):
        "Return an arbitrary value not of value_or_type"
        avoided_type = cls._type(value_or_type)
        different_type = lambda value: not isinstance(value, avoided_type)
        return filter(different_type, cls._all)

    @staticmethod
    def _type(value_or_type):
        "return expected type"
        if isinstance(value_or_type, type):
            return value_or_type
        else:
            return type(value_or_type)

class Paths:
    "methods that provide Paths for testing"

    _input_files_parent_directory = os.path.dirname(fixture_constants.__file__)
    _path_to_input_files = os.path.join(_input_files_parent_directory, 'input_files')

    @classmethod
    def basic_input_file(cls):
        "return the path to the basic input file"
        directory = cls._path_to_input_files
        file_name = fixture_constants.BasicInputFile.file_name
        return os.path.join(directory, file_name)

    @classmethod
    def advanced_input_file(cls):
        "return the path to the advanced input file"
        directory = cls._path_to_input_files
        file_name = fixture_constants.AdvancedInputFile.file_name
        return os.path.join(directory, file_name)

    @classmethod
    def parse(cls):
        "return the path to the parse application"
        directory = os.path.dirname(parse.__file__)
        file_name = 'parse'
        return os.path.join(directory, file_name)
