"Test Parse module"

import pytest
import subprocess

from parse.options import __doc__, __version__
import parse

from fixture_methods import Results, Paths

@pytest.fixture(params=(
        (Results.of_basic_input_file(), Paths.basic_input_file()),
        (Results.of_advanced_input_file(), Paths.advanced_input_file()),
        ))
def expectations_and_source(request):
    "return expected results and input path from which to find them"
    expected_results, path = request.param
    expected_results = '\n'.join(expected_results) + '\n'
    return expected_results, path

def test_stdin_and_stdout(expectations_and_source):
    "confirm Results parsed correctly from StdIn to StdOut"
    expected_results, input_path = expectations_and_source
    with open(input_path) as input_file:
        found_results = subprocess.check_output([Paths.parse(), '-'], stdin=input_file)
    assert expected_results == found_results

def test_in_path_and_stdout(expectations_and_source):
    "confirm Results parsed correctly from path to StdOut"
    expected_results, input_path = expectations_and_source
    found_results = subprocess.check_output([Paths.parse(), input_path])
    assert expected_results == found_results

def test_stdin_and_out_path(tmpdir, expectations_and_source):
    "confirm Results parsed correctly from StdIn to out_path"
    expected_results, input_path = expectations_and_source
    output_path = str(tmpdir.join('tmp_out_file'))
    with open(input_path) as input_file:
        subprocess.call([Paths.parse(), '-', output_path], stdin=input_file)
    with open(output_path) as parsed_results:
        found_results = parsed_results.read()
    assert expected_results == found_results

def test_in_path_and_out_path(tmpdir, expectations_and_source):
    "confirm Results parsed correctly from in_path to out_path"
    expected_results, input_path = expectations_and_source
    output_path = str(tmpdir.join('tmp_out_file'))
    subprocess.call([Paths.parse(), input_path, output_path])
    with open(output_path) as parsed_results:
        found_results = parsed_results.read()
    assert expected_results == found_results

def test_version():
    "confirm parse displays expected version"
    expected_version = ' '.join(('Kata Bank OCR Parser', 'version', __version__))
    found_version = subprocess.check_output([Paths.parse(), '--version']).rstrip('\n')
    assert expected_version == found_version

@pytest.mark.parametrize('argument', ('-h', '--help'))
def test_help(argument):
    "confirm parse --help displays expected docstring"
    expected_docstring = __doc__
    found_docstring = subprocess.check_output([Paths.parse(), argument])
    assert expected_docstring.split() == found_docstring.split()
