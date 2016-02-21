#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name = "mdtools",
    packages = find_packages(),

    entry_points = {
        'console_scripts': [
            'mdimg = mdimg:main',
            'mdslides = mdslides:main',
            'mddiff = diff:main',
        ],
    }

)
