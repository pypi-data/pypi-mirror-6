import codecs
import os
import re

from setuptools import setup


here = os.path.abspath(os.path.dirname(__file__))


# Adapted from https://github.com/pypa/sampleproject
#
# Read the version number from a source file.
# Why read it, and not import?
# see https://groups.google.com/d/topic/pypa-dev/0PkjVpcxTzQ/discussion
def find_version(*file_paths):
    # Open in Latin-1 so that we avoid encoding errors.
    # Use codecs.open for Python 2 compatibility
    with codecs.open(os.path.join(here, *file_paths), 'r', 'latin1') as f:
        version_file = f.read()

    # The version line must have the form
    # __version__ = 'ver'
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


with codecs.open('README.txt', encoding='utf-8') as f:
    long_description = f.read()


setup(
    name="dataschema",
    version=find_version('dataschema', 'dataschema.py'),
    description="Schema validation for Python data structures",
    long_description=long_description,

    url='https://pypi.python.org/pypi/dataschema/',

    author='Stefan W',
    author_email='stefan+pypi@geeky.net',

    license='MIT',

    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='data schema validation',

    packages=[
        'dataschema',
        'dataschema.tests',
        ],
    test_suite='dataschema.tests.test_dataschema',
)
