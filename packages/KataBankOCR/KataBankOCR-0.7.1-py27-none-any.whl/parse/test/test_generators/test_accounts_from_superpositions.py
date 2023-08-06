"test the accounts_from_superpositions generator"

import pytest

from parse.generators.accounts_from_superpositions import accounts_from_superpositions

import check_generator
from fixture_methods import Accounts, Superpositions

test_iterability = check_generator.raises_on_non_iterable(generator=accounts_from_superpositions)

test_element_type = \
    check_generator.raises_on_bad_element_type(generator=accounts_from_superpositions,
                                               value_or_type=dict)

accounts = Accounts.of_example_accounts() + Accounts.of_flawed_accounts()
superpositions = Superpositions.of_example_accounts() + Superpositions.of_flawed_accounts()

@pytest.mark.parametrize('expected_account, superpositions', (zip(accounts, superpositions)))
def test_known_superpositions_yield_expected_account(expected_account, superpositions):
    "confirm known superpositions yield expected accounts"
    iterator = accounts_from_superpositions(superpositions)
    found_accounts = list(iterator)
    assert [expected_account] == found_accounts
