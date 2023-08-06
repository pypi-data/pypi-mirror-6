"test the parse module's version and version_info"

import parse
from parse import version

def test_parse_version_matches_version_version():
    "confirm parse module has same version as version module"
    assert version.__version__ == parse.__version__

def test_parse_version_info_matches_version_version_info():
    "confirm parse module has same version_info as version module"
    assert version.__version_info__ == parse.__version_info__

def test_version_type():
    "confirm version a string"
    assert isinstance(parse.__version__, basestring)

def test_version_format():
    "confirm version contains three dot-delimited strings"
    assert len(parse.__version__.split('.')) == 3

def test_version_info_type():
    "confirm version_info a tuple"
    assert isinstance(parse.__version_info__, tuple)

def test_version_info_element_type():
    "confirm version_info composed of ints"
    for element in parse.__version_info__:
        assert isinstance(element, int)

def test_version_info_element_count():
    "confirm version_info contains 3 elements"
    assert len(parse.__version_info__) == 3

def test_version_matches_version_info():
    "confirm version composed of version_info in 3-dot notation"
    assert '.'.join(map(str, parse.__version_info__)) == parse.__version__
