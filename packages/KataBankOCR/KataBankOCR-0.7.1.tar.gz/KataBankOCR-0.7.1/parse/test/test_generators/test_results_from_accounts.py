"test the results_from_accounts generator"

import pytest

from parse.generators.results_from_accounts import results_from_accounts

import check_generator
from fixture_methods import Results, Accounts, Numerals

test_iterability = check_generator.raises_on_non_iterable(generator=results_from_accounts)

test_element_type = \
    check_generator.raises_on_bad_element_type(generator=results_from_accounts,
                                               value_or_type=basestring)

test_element_length = \
    check_generator.raises_on_bad_element_length(generator=results_from_accounts,
                                                 valid_element=Accounts.get_random())

test_element_composition = \
    check_generator.raises_on_bad_element_composition(generator=results_from_accounts,
                                                      valid_element=Accounts.get_random(),
                                                      adulterants=Numerals.invalid())

@pytest.mark.parametrize('expected_results, accounts', (
        (Results.of_example_accounts(), Accounts.of_example_accounts()),
        (Results.of_flawed_accounts(), Accounts.of_flawed_accounts()),
        ))
def test_parses_known_accounts_to_results(expected_results, accounts):
    "confirm known account recognized correctly"
    iterator = results_from_accounts(accounts)
    found_results = list(iterator)
    assert expected_results == found_results
