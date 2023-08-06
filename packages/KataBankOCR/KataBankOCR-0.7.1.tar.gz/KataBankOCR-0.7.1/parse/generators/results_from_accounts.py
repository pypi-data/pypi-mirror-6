"generator that yields Results and the functions that support it"

from parse import settings
from parse.validators import Validate

def results_from_accounts(accounts):
    "generator that consumes Accounts and yields Results"
    for account in accounts:
        _validate_account(account)
        status = _status_from_account(account)
        result = account + status
        yield result

def _validate_account(account):
    "confirm account type, length, and composition or raise ValueError"
    Validate.type(basestring, account, 'Account')
    Validate.length(settings.figures_per_entry, account, 'Account')
    expected_numerals = settings.valid_numerals | set(settings.illegible_numeral)
    Validate.composition(expected_numerals, account, 'Account')

def _status_from_account(account):
    "return appropriate status for the Account"
    if settings.illegible_numeral in account or not settings.checksum(account):
        return settings.ambiguous_status
    return ''  # Valid Account
