from setuptools import setup, find_packages
import codecs
import os
import re

here = os.path.abspath(os.path.dirname(__file__))

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

setup(
	# Project information
	name = 'pysander',
	version = find_version('pysander', '__init__.py'),
	description = 'A python framework for building RESTful crud APIs',
	url = 'https://bitbucket.org/lvanspronsen/pysander',

	# Author information
	author = 'Loren Van Spronsen',
	author_email = 'lorenvs@outlook.com',

	# Released under the MIT license
	license = 'MIT',

	# runtime dependencies
	install_requires = [
		'sqlalchemy',
		'flask'
	],

	# packages to install
	packages = ['pysander'],

	# Additional information
	classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 2.7',
    ]
)


