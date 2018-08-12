# -*- coding: utf-8 -*-
"""
Tests for mdslides

"""

import os

from tests.common import FileBasedTestCase


from slides.index import cmd_build_index_db
from slides.commands import get_parser
from slides.build_slides import (
    build_deckset_slides,
    build_reveal_slides,
    build_wordpress,
    SectionCompiler,
)
from slides.ebook_builder import EbookWriter

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
        self.compare_results(self.tmp_path('title.md'),
                             make_path('compiled', 'title.md'))
        self.compare_results(self.tmp_path('introduction.md'),
                             make_path('compiled', 'introduction.md'))
        self.compare_results(self.tmp_path('images.md'),
                             make_path('compiled', 'images.md'))
        self.compare_results(self.tmp_path('text.md'),
                             make_path('compiled', 'text.md'))
        self.compare_results(self.tmp_path('appendix.md'),
                             make_path('compiled', 'appendix.md'))

    def test_build_index_db(self):
        """The index-db is build correctly from structure.yaml."""

        index_db = self.tmp_path('index-db.yaml')
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
                                       make_path('compiled'),
                                       self.tmp_path('slides.html'),
                                       '--template', make_path('templates', 'revealjs-template.html'),
                                       '--glossary', make_path('glossary.yaml'),
                                       '--glossary-items', '2',
                                       '--section-prefix', "Section %(chapter)s.%(section)s:",
                                       ])

        build_reveal_slides(args)
        self.compare_results(self.tmp_path('slides.html'),
                             make_path('slides.html'))

    def test_build_deckset(self):
        """Build markdown for deckset from output of compile step."""
        args = self.parser.parse_args(['build', 'deckset',
                                       make_path('structure.yaml'),
                                       make_path('compiled'),
                                       self.tmp_path('deckset.md'),
                                       '--template', make_path('templates', 'deckset-template.md'),
                                       '--glossary', make_path('glossary.yaml'),
                                       '--glossary-items', '2',
                                       '--section-prefix', "Section %(chapter)s.%(section)s:",
                                       ])
        build_deckset_slides(args)
        self.compare_results(self.tmp_path('deckset.md'),
                             make_path('deckset.md'))

    def test_build_wordpress(self):
        """Build markdown for wordpress from output of compile step."""
        args = self.parser.parse_args(['build', 'wordpress',
                                       make_path('structure.yaml'),
                                       make_path('compiled'),
                                       self.document_root,
                                       '--footer', make_path('templates', 'wordpress-footer.txt'),
                                       '--glossary', make_path('glossary.yaml'),
                                       '--section-prefix', "Section %(chapter)s.%(section)s:",
                                       ])

        build_wordpress(args)
        self.compare_results(self.tmp_path('title.md'),
                             make_path('wordpress', 'title.md'))
        self.compare_results(self.tmp_path('introduction.md'),
                             make_path('wordpress', 'introduction.md'))
        self.compare_results(self.tmp_path('images.md'),
                             make_path('wordpress', 'images.md'))
        self.compare_results(self.tmp_path('text.md'),
                             make_path('wordpress', 'text.md'))
        self.compare_results(self.tmp_path('appendix.md'),
                             make_path('wordpress', 'appendix.md'))

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
                                       '--index', make_path('index-db.yaml'),
                                       '--section-prefix', "Section %(chapter)s.%(section)s:",
                                       ])

        e = EbookWriter(args)
        e.build()
        self.compare_results(self.tmp_path('tmp-introduction.md'),
                             make_path('ebook', 'tmp-introduction.md'))
        self.compare_results(self.tmp_path('tmp-chapters.md'),
                             make_path('ebook', 'tmp-chapters.md'))
        self.compare_results(self.tmp_path('tmp-appendix.md'),
                             make_path('ebook', 'tmp-appendix.md'))

