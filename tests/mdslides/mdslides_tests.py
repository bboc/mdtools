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
        args = self.parser.parse_args(['compile',
                                      '--glossary', make_path('glossary.yaml'),
                                       make_path('structure.yaml'),
                                       make_path('content', 'src'),
                                       self.document_root
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
