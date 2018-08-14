# -*- coding: utf-8 -*-
"""
Tests for reading the config and building in-memory objects

"""

import os


import yaml
from textwrap import dedent
from unittest import TestCase

from slides.common import parse_config


class ConfigTests(TestCase):

    result = {
        'content': {'appendix': {'sections': [{'slug': 'glossary',
                                               'title': 'Glossary'},
                                              {'slug': 'changelog',
                                               'title': 'Changelog'},
                                              {'slug': 'license',
                                               'title': 'License'}],
                                 'slug': 'appendix',
                                 'title': 'Appendix'},
                    'chapters': [{'sections': [{'slug': 'deckset',
                                                'title': 'Deckset'},
                                               {'slug': 'jekyll',
                                                'title': 'Jekyll'}],
                                  'slug': 'formats',
                                  'title': 'Formats'},
                                 {'sections': [{'slug': 'glossary entries',
                                                'title': 'Glossary Entries'},
                                               {'slug': 'section-links',
                                                'title': 'Section Links'},
                                               {'slug': 'chapter-headers',
                                                'title': 'Chapter Headers'},
                                               {'slug': 'index-files',
                                                'title': 'Index Files'}],
                                  'slug': 'features',
                                  'title': 'Features'},
                                 {'sections': [{'slug': 'templates',
                                                'title': 'Templates'}],
                                  'slug': 'data-structure',
                                  'title': 'Data Structure'},
                                 {'sections': [{'slug': 'mdslides',
                                                'title': 'Mdslides'},
                                               {'slug': 'mdimg',
                                                'title': 'Mdimg'}],
                                  'slug': 'commands',
                                  'title': 'Commands'},
                                 {'sections': [{'slug': 'translating-templates',
                                                'title': 'Translating Templates'}],
                                  'slug': 'translation',
                                  'title': 'Translation'}],
                    'end': 'SKIP',
                    'introduction': {'sections': [{'slug': 'overview',
                                                   'title': 'Overview'},
                                                  {'slug': 'usecases',
                                                   'title': 'Usecases'}],
                                     'slug': 'introduction',
                                     'title': 'Introduction'},
                    'title': 'title'},
        'section-prefix': '%(chapter)s.%(section)s:'}

    def test_new_format(self):
        """Config in new format is properly parsed"""
        cfg = dedent("""

          section-prefix: "%(chapter)s.%(section)s:"
          content:
            title: title
            end: SKIP
            introduction:
              title: Introduction
              slug: introduction
              sections:
                - overview
                - usecases
            chapters:
              - formats:
                - deckset
                - jekyll
              - features:
                - title: Glossary Entries
                  slug: glossary entries
                - section links
                - chapter headers
                - index files
              - title: Data Structure
                slug: data-structure
                sections:
                  - title: Templates
                    slug: templates
              - commands:
                - mdslides
                - mdimg
              - translation:
                - translating templates
            appendix:
              - glossary
              - changelog
              - license
         """)
        parsed = parse_config(yaml.load(cfg))
        # import pprint
        # pprint.pprint(parsed)
        # pprint.pprint(self.result)
        self.failUnlessEqual(parsed, self.result)

    def test_old_format(self):
        #self.maxDiff = None
        cfg = dedent("""
            title: title
            end: SKIP

            section-prefix: "%(chapter)s.%(section)s:"

            introduction:
              - overview
              - usecases

            appendix:
              - glossary
              - changelog
              - license

            chapter-order:
              - formats
              - features
              - data structure
              - commands
              - translation

            chapters:
              formats:
                - deckset
                - jekyll
              features:
                - glossary entries
                - section links
                - chapter headers
                - index files
              data structure:
                - templates
              commands:
                - mdslides
                - mdimg
              translation:
                - translating templates
        """)
        parsed = parse_config(yaml.load(cfg))
        import pprint
        pprint.pprint(parsed)
        pprint.pprint(self.result)
        self.failUnlessEqual(parsed, self.result)
