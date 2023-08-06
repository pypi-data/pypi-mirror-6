" Static values that restate kata.txt "

# An Entry contains a defined number of Lines from an input File.
lines_per_entry = 4
# An Entry represents an Account composed of Numerals
# The four Lines in this example Entry represent the Account '123456789'
'    _  _     _  _  _  _  _ '
'  | _| _||_||_ |_   ||_||_|'
'  ||_  _|  | _||_|  ||_| _|'
'                           '
# All Entries contain the same number of Figures
figures_per_entry = 9
# A Figure consist of Strokes and represents a Numeral
# The Figure in this example represents the Numeral '5'
' _ '
'|_ '
' _|'
'   '
# A Figure results from the joining of vertically adjacent Substrings within an Entry
# All Substrings have a known length
strokes_per_substring = 3
# All Lines have a known length
strokes_per_line = strokes_per_substring * figures_per_entry
# All Figures have a known length
strokes_per_figure = strokes_per_substring * lines_per_entry
# All Figures contain only of valid Strokes
valid_strokes = set('_ |')
# All Numerals consist of a single digit string
valid_numerals = set('0123456789')
# All known Figures uniquely represent a unique Numeral
figures = {' _ ' +
           '| |' +
           '|_|' +
           '   ': '0',
           '   ' +
           '  |' +
           '  |' +
           '   ': '1',
           ' _ ' +
           ' _|' +
           '|_ ' +
           '   ': '2',
           ' _ ' +
           ' _|' +
           ' _|' +
           '   ': '3',
           '   ' +
           '|_|' +
           '  |' +
           '   ': '4',
           ' _ ' +
           '|_ ' +
           ' _|' +
           '   ': '5',
           ' _ ' +
           '|_ ' +
           '|_|' +
           '   ': '6',
           ' _ ' +
           '  |' +
           '  |' +
           '   ': '7',
           ' _ ' +
           '|_|' +
           '|_|' +
           '   ': '8',
           ' _ ' +
           '|_|' +
           ' _|' +
           '   ': '9'}
# All other Figures yield the illegible Numeral
illegible_numeral = '?'

# The Checksum function differentiates between a 'valid' and an 'invalid' Account
def checksum(account):
    """ return True for a valid Acount and False for an invalid Account
    account number:  3  4  5  8  8  2  8  6  5
    position names:  d9 d8 d7 d6 d5 d4 d3 d2 d1
    checksum calculation: (d1+2*d2+3*d3 +..+9*d9) mod 11 = 0 """
    values = [int(numeral) * (9 - index) for index, numeral in enumerate(account)]
    return sum(values).__mod__(11) == 0
# The Checksum function will return True for each of these Accounts
some_known_valid_accounts = ('123456789', '490867715', '899999999',
                             '000000051', '686666666', '559555555')
# The Checksum function will return False for each of these Accounts
some_known_invalid_accounts = ('490067715', '888888888', '555555555',
                               '333333333', '111111111', '777777777')

# A Result includes an Account and, if not valid, a Status

# Some Entries may contain one or more flawed Figures.
# A flawed Figure does not directly represent a valid Numeral due to missing or additional strokes.
# A Superposition represents the relationship between a Figure and all possible Numerals.
# A Superposition tracks how many strokes one must add or remove to properly represent a Numeral.
# A collection of Superpositions, one for each Figure in an Entry, represents one or more Accounts.

# When a collection of Superpositions does not represent one account better than all others,
#   (ie: with fewer missing/additional Strokes required for that Account than all others),
#   then the Result for that Entry will include the Ambiguous Status.
ambiguous_status = ' AMB'
