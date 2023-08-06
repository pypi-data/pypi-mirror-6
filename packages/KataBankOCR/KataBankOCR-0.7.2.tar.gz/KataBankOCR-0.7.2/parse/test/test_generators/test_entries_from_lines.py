"Test the entries_from_lines generator"

import pytest

from parse import settings
from parse.generators.entries_from_lines import entries_from_lines

import check_generator
from fixture_methods import Entries, Lines

test_iterability = check_generator.raises_on_non_iterable(generator=entries_from_lines)

def test_known_lines_grouped_to_known_entries():
    "confirm known lines grouped into known entries"
    expected_entries = Entries.of_basic_input_file()
    lines = Lines.of_basic_input_file()
    found_entries = list(entries_from_lines(lines))
    assert expected_entries == found_entries

if settings.lines_per_entry > 1:
    def test_insufficient_line_count_raises_expected_error():
        "confirm a truncated list of lines raises appropriate error"
        lines = Lines.of_basic_input_file()
        truncated_lines = lines[:-1]
        iterator = entries_from_lines(truncated_lines)
        pytest.raises(ValueError, list, iterator)
        message = 'File ended mid-entry'
