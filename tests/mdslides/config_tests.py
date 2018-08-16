# -*- coding: utf-8 -*-
"""
Tests for reading the config and building in-memory objects

"""

import yaml
from textwrap import dedent
import unittest

from slides.common import parse_config, parse_config_new, Section, Content


class ConfigTests(unittest.TestCase):

    result = {
        'content': {'appendix': {'sections': [{'id': 1,
                                               'slug': 'glossary',
                                               'title': 'Glossary'},
                                              {'id': 2,
                                               'slug': 'changelog',
                                               'title': 'Changelog'},
                                              {'id': 3,
                                               'slug': 'license',
                                               'title': 'License'}],
                                 'slug': 'appendix',
                                 'title': 'Appendix'},
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
                                  'title': 'Formats'},
                                 {'id': 2,
                                  'sections': [{'chapter_id': 2,
                                                'id': 1,
                                                'slug': 'glossary-entries',
                                                'title': 'Glossary Entries'},
                                               {'chapter_id': 2,
                                                'id': 2,
                                                'slug': 'section-links',
                                                'title': 'Section Links'},
                                               {'chapter_id': 2,
                                                'id': 3,
                                                'slug': 'chapter-headers',
                                                'title': 'Chapter Headers'},
                                               {'chapter_id': 2,
                                                'id': 4,
                                                'slug': 'index-files',
                                                'title': 'Index Files'}],
                                  'slug': 'features',
                                  'title': 'Features'},
                                 {'id': 3,
                                  'sections': [{'chapter_id': 3,
                                                'id': 1,
                                                'slug': 'templates',
                                                'title': 'Templates'}],
                                  'slug': 'data-structure',
                                  'title': 'Data Structure'},
                                 {'id': 4,
                                  'sections': [{'chapter_id': 4,
                                                'id': 1,
                                                'slug': 'mdslides',
                                                'title': 'Mdslides'},
                                               {'chapter_id': 4,
                                                'id': 2,
                                                'slug': 'mdimg',
                                                'title': 'Mdimg'}],
                                  'slug': 'commands',
                                  'title': 'Commands'},
                                 {'id': 5,
                                  'sections': [{'chapter_id': 5,
                                                'id': 1,
                                                'slug': 'translating-templates',
                                                'title': 'Translating Templates'}],
                                  'slug': 'translation',
                                  'title': 'Translation'}],
                    'end': 'SKIP',
                    'introduction': {'sections': [{'id': 1,
                                                   'slug': 'overview',
                                                   'title': 'Overview'},
                                                  {'id': 2,
                                                   'slug': 'usecases',
                                                   'title': 'Usecases'}],
                                     'slug': 'introduction',
                                     'title': 'Introduction'},
                    'title': 'title'},
        'index': [{'chapter_id': 2,
                   'id': 3,
                   'slug': 'chapter-headers',
                           'title': 'Chapter Headers'},
                  {'chapter_id': 1,
                   'id': 1,
                   'slug': 'deckset',
                           'title': 'Deckset'},
                  {'chapter_id': 2,
                   'id': 1,
                   'slug': 'glossary-entries',
                           'title': 'Glossary Entries'},
                  {'chapter_id': 2,
                   'id': 4,
                   'slug': 'index-files',
                           'title': 'Index Files'},
                  {'chapter_id': 1,
                   'id': 2,
                   'slug': 'jekyll',
                           'title': 'Jekyll'},
                  {'chapter_id': 4,
                   'id': 2,
                   'slug': 'mdimg',
                           'title': 'Mdimg'},
                  {'chapter_id': 4,
                   'id': 1,
                   'slug': 'mdslides',
                           'title': 'Mdslides'},
                  {'chapter_id': 2,
                   'id': 2,
                   'slug': 'section-links',
                           'title': 'Section Links'},
                  {'chapter_id': 3,
                   'id': 1,
                   'slug': 'templates',
                           'title': 'Templates'},
                  {'chapter_id': 5,
                   'id': 1,
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


class SectionTests(unittest.TestCase):

    def test_old_style_section(self):

        s = Section.from_config('some section name')

        self.failUnlessEqual(s.to_dict(), {
            'title': 'Some Section Name',
            'slug': 'some-section-name',
            'id': None,
            'chapter_id': None})

    def test_new_style_section(self):

        s = Section.from_config({
            'title': 'Some Section Name',
            'slug': 'some-section-name'})

        self.failUnlessEqual(s.to_dict(), {
            'title': 'Some Section Name',
            'slug': 'some-section-name',
            'id': None,
            'chapter_id': None})

class PartTests(unittest.TestCase):
    pass




class ChapterTests(unittest.TestCase):
    def test_new_style_chapter(self):

        data = parse_config_new(yaml.load("""
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
            """))



class InheritaceTests(unittest.TestCase):

    def test_it(self):

        class Base(object):

            @classmethod
            def foo(cls):
                print 'base'
                return cls()

        class Child(Base):
            @classmethod
            def foo(cls):
                print 'chi;ld'
                return super(Child, cls).foo()
        base = Base.foo()
        child = Child.foo()

        print 'basetype', type(base)
        print 'childtype', type(child)
        self.failUnless(isinstance(base, Base))
        self.failUnless(isinstance(child, Base))

        self.failUnless(isinstance(child, Child))

class ContentTests(unittest.TestCase):

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
        c = Content.from_config(yaml.load(cfg))
        import pprint
        pprint.pprint(c.to_dict())
        pprint.pprint(self.result)
        self.failUnlessEqual(c.to_dict(), self.result)



