#!/usr/bin/env python
import os
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


# TODO: make a nicer setup.py from https://github.com/navdeep-G/setup.py
setup(
    name="mdtools",
    version='2.0.0',
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*", "tests.*"]),
    install_requires=['polib'],
    author="Bernhard Bockelbrink",
    author_email="bernhard.bockelbrink@gmail.com",
    description="A commandline tools for publishing various document formats (Jekyll, LaTeX, ePub etc.) from a single markdown source.",
    long_description=read("README.md"),
    keywords="single-source-publishing Markdown reveal.js slide-decks i18n LaTeX ePub Multimarkdown Jekyll GitHub-pages",
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
            'mdbuild = mdbuild.main:main_build',
            'mdtemplate = mdbuild.main:main_template',
            'mdimg = mdimg.command:main',
            'mddiff = diff:main',
            # TODO: fix commands and activate
            # 'mdskeleton = mdbuild.build.sekeleton:main',
            # 'mdconvert = mdbuild.main:main_convert',
        ],
    }

)
