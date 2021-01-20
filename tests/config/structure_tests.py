# -*- coding: utf-8 -*-

import unittest

from slides.config import Content


class TestStructure(unittest.TestCase):

    def test_simple_structure(self):
        c = Content.from_config({
            'config': {},
            'parts': [
                {
                    'id': 'introduction',
                },
                {
                    'id': 'part 2',
                    'chapters': [
                        {
                            "id": "chapter 1",
                            "tags": ['foo', 'bar'],
                            'sections': [
                                {
                                    'id': 'section 1',
                                    'tags': ['foo'],
                                },
                                {
                                    'id': 'section 2',
                                    'config': {
                                        'param1': 'value1',
                                        'param2': 'value2',
                                    }
                                },
                            ],
                        },
                        {
                            "id": "chapter 2",
                        },
                    ],
                },
                {
                    'id': 'appendix',
                    'chapters': [
                        {
                            "id": "chapter 1",
                        },
                        {
                            "id": "chapter 2",
                        },
                    ],
                },
            ]}, '/')
        c.to_dict()
