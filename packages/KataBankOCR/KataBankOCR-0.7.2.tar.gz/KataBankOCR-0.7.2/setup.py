from __future__ import print_function
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import io
import codecs
import os
import sys

here = os.path.abspath(os.path.dirname(__file__))

def read(*filenames, **kwargs):
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n')
    buf = []
    for filename in filenames:
        with io.open(filename, encoding=encoding) as f:
            buf.append(f.read())
    return sep.join(buf)

long_description = read('README.rst',)
execfile('parse/version.py')

class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        error_code = pytest.main(['-k', 'parse/test/test_settings.py'])
        if error_code:
            sys.exit(errcode)
        errcode = pytest.main(self.test_args)
        sys.exit(errcode)

setup(
    name='KataBankOCR',
    version=__version__,
    url='https://github.com/gJigsaw/KataBankOCR',
    license='GNU General Public License',
    author='Jason Green',
    tests_require=['pytest', 'docopt'],
    install_requires=['docopt>=0.6.1'],
    cmdclass={'test': PyTest},
    author_email='KataBankOCR@JasonGreen.Name',
    description='Programming kata to parse output from fictitious OCR machine',
    long_description=long_description,
    packages=find_packages(exclude=['test_*']),
    include_package_data=True,
    platforms='any',
    test_suite='test',
    classifiers=[
        'Programming Language :: Python',
        'Development Status :: 4 - Beta',
        'Natural Language :: English',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
        ],
    extras_require={'testing': ['pytest']},
    scripts=['parse/parse'],
)
