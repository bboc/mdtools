# -*- coding: utf-8 -*-
"""
Tests for reading the config and building in-memory objects

"""

import yaml
from textwrap import dedent
from unittest import TestCase

from slides.common import parse_config


class ConfigTests(TestCase):

    result = {
        'content': {'appendix': {'sections': [{'index': 1,
                                               'slug': 'glossary',
                                               'title': 'Glossary'},
                                              {'index': 2,
                                               'slug': 'changelog',
                                               'title': 'Changelog'},
                                              {'index': 3,
                                               'slug': 'license',
                                               'title': 'License'}],
                                 'slug': 'appendix',
                                 'title': 'Appendix'},
                    'chapters': [{'index': 1,
                                  'sections': [{'chapter-index': 1,
                                                'index': 1,
                                                'slug': 'deckset',
                                                'title': 'Deckset'},
                                               {'chapter-index': 1,
                                                'index': 2,
                                                'slug': 'jekyll',
                                                'title': 'Jekyll'}],
                                  'slug': 'formats',
                                  'title': 'Formats'},
                                 {'index': 2,
                                  'sections': [{'chapter-index': 2,
                                                'index': 1,
                                                'slug': 'glossary-entries',
                                                'title': 'Glossary Entries'},
                                               {'chapter-index': 2,
                                                'index': 2,
                                                'slug': 'section-links',
                                                'title': 'Section Links'},
                                               {'chapter-index': 2,
                                                'index': 3,
                                                'slug': 'chapter-headers',
                                                'title': 'Chapter Headers'},
                                               {'chapter-index': 2,
                                                'index': 4,
                                                'slug': 'index-files',
                                                'title': 'Index Files'}],
                                  'slug': 'features',
                                  'title': 'Features'},
                                 {'index': 3,
                                  'sections': [{'chapter-index': 3,
                                                'index': 1,
                                                'slug': 'templates',
                                                'title': 'Templates'}],
                                  'slug': 'data-structure',
                                  'title': 'Data Structure'},
                                 {'index': 4,
                                  'sections': [{'chapter-index': 4,
                                                'index': 1,
                                                'slug': 'mdslides',
                                                'title': 'Mdslides'},
                                               {'chapter-index': 4,
                                                'index': 2,
                                                'slug': 'mdimg',
                                                'title': 'Mdimg'}],
                                  'slug': 'commands',
                                  'title': 'Commands'},
                                 {'index': 5,
                                  'sections': [{'chapter-index': 5,
                                                'index': 1,
                                                'slug': 'translating-templates',
                                                'title': 'Translating Templates'}],
                                  'slug': 'translation',
                                  'title': 'Translation'}],
                    'end': 'SKIP',
                    'introduction': {'sections': [{'index': 1,
                                                   'slug': 'overview',
                                                   'title': 'Overview'},
                                                  {'index': 2,
                                                   'slug': 'usecases',
                                                   'title': 'Usecases'}],
                                     'slug': 'introduction',
                                     'title': 'Introduction'},
                    'title': 'title'},
        'section-index': [{'chapter-index': 2,
                           'index': 3,
                           'slug': 'chapter-headers',
                           'title': 'Chapter Headers'},
                          {'chapter-index': 1,
                           'index': 1,
                           'slug': 'deckset',
                           'title': 'Deckset'},
                          {'chapter-index': 2,
                           'index': 1,
                           'slug': 'glossary-entries',
                           'title': 'Glossary Entries'},
                          {'chapter-index': 2,
                           'index': 4,
                           'slug': 'index-files',
                           'title': 'Index Files'},
                          {'chapter-index': 1,
                           'index': 2,
                           'slug': 'jekyll',
                           'title': 'Jekyll'},
                          {'chapter-index': 4,
                           'index': 2,
                           'slug': 'mdimg',
                           'title': 'Mdimg'},
                          {'chapter-index': 4,
                           'index': 1,
                           'slug': 'mdslides',
                           'title': 'Mdslides'},
                          {'chapter-index': 2,
                           'index': 2,
                           'slug': 'section-links',
                           'title': 'Section Links'},
                          {'chapter-index': 3,
                           'index': 1,
                           'slug': 'templates',
                           'title': 'Templates'},
                          {'chapter-index': 5,
                           'index': 1,
                           'slug': 'translating-templates',
                           'title': 'Translating Templates'}],
        'section-prefix': '%(chapter)s.%(section)s:'}

    def test_new_format(self):
        """Config in new format is properly parsed"""
        self.maxDiff = None
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
                          slug: glossary-entries
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
        import pprint
        pprint.pprint(parsed)
        pprint.pprint(self.result)
        self.failUnlessEqual(parsed, self.result)

    def test_old_format(self):
        self.maxDiff = None
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
