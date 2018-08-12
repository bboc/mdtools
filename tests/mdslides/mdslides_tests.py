# -*- coding: utf-8 -*-
"""
Tests for mdslides

"""

import os

from tests.common import FileBasedTestCase


from slides.index import cmd_build_index_db
from slides.commands import get_parser
from slides.build_slides import SectionCompiler


def data_dir():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        'test-data')


def make_path(*args):
    return os.path.join(data_dir(), *args)


class CompileSlidesTests(FileBasedTestCase):

    def setUp(self):
        super(CompileSlidesTests, self).setUp()
        self.parser = get_parser()

    def test_compile_slides(self):
        """Slides are correctly compiled into chapters."""
        args = self.parser.parse_args(['compile',
                                       make_path('structure.yaml'),
                                       make_path('content', 'src'),
                                       self.document_root,
                                      '--glossary', make_path('glossary.yaml'),
                                       ])
        c = SectionCompiler(args)
        c.compile_content()
        self.compare_results(os.path.join(self.document_root, 'title.md'),
                             make_path('sections-compiled', 'title.md'))
        self.compare_results(os.path.join(self.document_root, 'introduction.md'),
                             make_path('sections-compiled', 'introduction.md'))
        self.compare_results(os.path.join(self.document_root, 'images.md'),
                             make_path('sections-compiled', 'images.md'))
        self.compare_results(os.path.join(self.document_root, 'text.md'),
                             make_path('sections-compiled', 'text.md'))
        self.compare_results(os.path.join(self.document_root, 'appendix.md'),
                             make_path('sections-compiled', 'appendix.md'))

    def test_build_index_db(self):
        """The index-db is build correctly from structure.yaml."""

        index_db = os.path.join(self.document_root, 'index-db.yaml')
        args = self.parser.parse_args(['build-index-db',
                                      make_path('structure.yaml'),
                                      index_db])

        cmd_build_index_db(args)

        self.assertTrue(os.path.exists(index_db))
        self.compare_results(index_db, make_path('index-db.yaml'))

    def test_build_reveal_js(self):
        """Build reveal.js slide deck from output of compile step."""
        args = self.parser.parse_args(['build', 'revealjs',
                                       make_path('structure.yaml'),
                                       make_path('content', 'src'),
                                       os.path.join(self.document_root, 'slides.html'),
                                       '--template', 'foo',
                                       '--glossary', make_path('glossary.yaml'),
                                       '--index', 'foo',
                                       '--glossary-items', '2',
                                       '--section-prefix', "Pattern %(chapter)s.%(section)s:",
                                       ])

        self.fail("not implemented")

    def test_build_deckset(self):
        """Build markdown for deckset from output of compile step."""
        args = self.parser.parse_args(['build', 'deckset',
                                       make_path('structure.yaml'),
                                       make_path('content', 'src'),
                                       self.document_root,
                                       '--template', 'foo',
                                       '--glossary', make_path('glossary.yaml'),
                                       '--index', 'foo',
                                       '--glossary-items', '2',
                                       '--section-prefix', "Pattern %(chapter)s.%(section)s:",
                                       ])

        self.fail("not implemented")

    def test_build_wordpress(self):
        """Build markdown for wordpress from output of compile step."""
        args = self.parser.parse_args(['build', 'wordpress',
                                       make_path('structure.yaml'),
                                       make_path('content', 'src'),
                                       self.document_root,
                                       '--footer', 'foo',
                                       '--glossary', make_path('glossary.yaml'),
                                       '--index', 'foo',
                                       '--section-prefix', "Section %(chapter)s.%(section)s:",
                                       ])

        self.fail("not implemented")

    def test_build_jekyll_site(self):
        """Jekyll site is built from source files."""
        args = self.parser.parse_args(['build', 'jekyll',
                                       make_path('structure.yaml'),
                                       make_path('content', 'src'),
                                       self.document_root,
                                       '--template', 'foo',
                                       '--glossary', make_path('glossary.yaml'),
                                       '--index', 'foo',
                                       '--glossary-items', '2',
                                       '--section-prefix', "Section %(chapter)s.%(section)s:",
                                       '--section-index-template', 'foo',
                                       '--introduction-template', 'foo',
                                       ])

        self.fail("not implemented")

    def test_build_ebook(self):
        """Ebook master is build from source."""
        args = self.parser.parse_args(['build', "ebook",
                                       make_path('structure.yaml'),
                                       make_path('content', 'src'),
                                       self.document_root,
                                       '--glossary', make_path('glossary.yaml'),
                                       '--index', 'foo',
                                       '--section-prefix', "Section %(chapter)s.%(section)s:",
                                       ])

        self.fail("not implemented")
