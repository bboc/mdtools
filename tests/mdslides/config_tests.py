# -*- coding: utf-8 -*-
"""
Tests for reading the config and building in-memory objects
"""

import yaml
import unittest

from slides.config import parse_config, Section, Content
from config_test_data import result, simple_format, extended_format


class ConfigTests(unittest.TestCase):

    def test_new_format(self):
        """Config in new format is properly parsed into structure object, rest of config is preserved."""
        self.maxDiff = None
        parsed = parse_config(yaml.load(extended_format))

        parsed['content'] = parsed['content'].to_dict()
        self.failUnlessEqual(parsed, result)

    def test_old_format(self):
        self.maxDiff = None
        parsed = parse_config(yaml.load(simple_format))
        import pprint
        pprint.pprint(parsed)
        parsed['content'] = parsed['content'].to_dict()
        self.failUnlessEqual(parsed, result)


class SectionTests(unittest.TestCase):

    def test_old_style_section(self):

        s = Section.from_config('some section name')

        self.failUnlessEqual(s.to_dict(), {
            'title': 'Some Section Name',
            'slug': 'some-section-name',
            'id': None})

    def test_new_style_section(self):

        s = Section.from_config({
            'title': 'Some Section Name',
            'slug': 'some-section-name'})

        self.failUnlessEqual(s.to_dict(), {
            'title': 'Some Section Name',
            'slug': 'some-section-name',
            'id': None})


class ContentTests(unittest.TestCase):

    def test_old_format(self):
        self.maxDiff = None
        c = Content.from_config(yaml.load(simple_format))
        self.failUnlessEqual(c.to_dict(), result['content'])

    def test_new_format(self):
        """Config in new format is properly parsed"""
        self.maxDiff = None

        c = Content.from_config(yaml.load(extended_format))
        self.failUnlessEqual(c.to_dict(), result['content'])

    def test_no_introduction_and_appendix(self):
        """Content must build when there is no introduction."""
        self.maxDiff = None

        c = Content.from_config(yaml.load("""
            content:
                chapters:
                    - formats:
                        - deckset
                        - jekyll
            """))
        self.failUnlessEqual(c.to_dict(), {
            'chapters': [{'id': 1,
                          'sections': [{'chapter_id': 1,
                                        'id': 1,
                                        'slug': 'deckset',
                                        'title': 'Deckset'},
                                       {'chapter_id': 1,
                                        'id': 2,
                                        'slug': 'jekyll',
                                        'title': 'Jekyll'}],
                          'slug': 'formats',
                          'title': 'Formats'}],
            'index': [
                {'chapter_id': 1,
                 'id': 1,
                 'slug': 'deckset',
                 'title': 'Deckset'},

                {'chapter_id': 1,
                 'id': 2,
                 'slug': 'jekyll',
                 'title': 'Jekyll'},
            ],
            'appendix': None,
            'introduction': None,
            'end': None,
            'title': None,

        })
