#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name = "mdtools",
    packages = find_packages(),

    entry_points = {
        'console_scripts': [
            'md-img-update = image_update:main',
        ],
    }

)
