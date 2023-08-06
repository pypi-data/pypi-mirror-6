"test the lines_from_path generator"

import pytest

from parse import settings
from parse.generators.lines_from_path import lines_from_path

from fixture_methods import Accounts, Paths

def test_with_bad_path():
    "confirm a bad path raises an expected error"
    iterator = lines_from_path('bad_path_string')
    pytest.raises((OSError, IOError,), list, iterator)

def test_line_count():
    "confirm all Lines read"
    accounts = Accounts.of_basic_input_file()
    expected_line_count = len(accounts) * settings.lines_per_entry
    iterator = lines_from_path(Paths.basic_input_file())
    found_line_count = len(list(iterator))
    assert expected_line_count == found_line_count
