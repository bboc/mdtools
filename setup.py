#!/usr/bin/env python
import os
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="mdtools",
    packages=find_packages(),
    author="Bernhard Bockelbrink",
    author_email="bernhard.bockelbrink@gmail.com",
    description="A set of commandline tools to maipulate and publish markdown files in various formats.",
    long_description=read("README.md"),
    keywords="Markdown reveal.js slide-decks i18n",
    url="https://github.com/bboc/mdtools",
    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Development Status :: 4 - Beta",
        'Operating System :: MacOS :: MacOS X',
        "Environment :: Console",
        "Programming Language :: Python :: 2.7",
        "Topic :: Utilities"
    ],

    entry_points={
        'console_scripts': [
            'mdimg = mdimg.command:main',
            'mdslides = slides.commands:main',
            'mddiff = diff:main',
        ],
    }

)
