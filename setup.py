#!/usr/bin/env python
import os
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="mdtools",
    packages=find_packages(),
    install_requires=['polib'],
    author="Bernhard Bockelbrink",
    author_email="bernhard.bockelbrink@gmail.com",
    description="A commandline tools for publishing various document formats (Jekyll, LaTeX, ePub etc.) from a single markdown source.",
    long_description=read("README.md"),
    keywords="Markdown reveal.js slide-decks i18n LaTeX EPUB Multimarkdown Jekyll",
    url="https://github.com/bboc/mdtools",
    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Development Status :: 4 - Beta",
        'Operating System :: MacOS :: MacOS X',
        "Environment :: Console",
        "Programming Language :: Python :: 3.0",
        "Topic :: Utilities"
    ],

    entry_points={
        'console_scripts': [
            'mdimg = mdimg.command:main',
            'mdbuild = mdbuild.main:main',
            'mddiff = diff:main',
        ],
    }

)
