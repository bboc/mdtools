#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name = "mdtools",
    packages = find_packages(),

    entry_points = {
        'console_scripts': [
            'mdimg = mdimg.command:main',
            'mdslides = slides.commands:main',
            'mddiff = diff:main',
        ],
    }

)
