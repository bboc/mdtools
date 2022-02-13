# -*- coding: utf-8 -*-

import unittest

from mdbuild.renderer import MetadataFilter


class TestMetadataFilter(unittest.TestCase):

    def _run_filter(self, target_format=None):
        return [line for line in MetadataFilter.filter(iter(self.input), target_format=target_format)]


class TestMetadataFilterBasics(TestMetadataFilter):

    def setUp(self):

        self.input = [
            '# my headline',
            '',
            '<summary>',
            'this is my summary',
            '</summary>',
            '',
            'some text'
        ]

    def test_empty_file(self):
        self.input = []
        res = self._run_filter()
        self.assertEqual(res, [])

    def test_title_and_summary(self):
        """Title and summary are extracted properly."""
        self._run_filter()
        self.assertEqual(MetadataFilter.title, 'my headline')
        self.assertEqual(MetadataFilter.summary, 'this is my summary')

        # if summary is enclosed in **, markup is removed properly
        self.input[3] = '**this is my summary**'
        res = self._run_filter(target_format="preserve")
        self.assertEqual(MetadataFilter.summary, 'this is my summary')
        self.assertEqual(res, [
            '# my headline',
            '',
            '<summary>',
            '**this is my summary**',
            '</summary>',
            '',
            'some text'
        ])

    def test_summary_format_html(self):
        res = self._run_filter(target_format='html')
        self.assertEqual(MetadataFilter.summary, 'this is my summary')
        self.assertEqual(res, [
            '# my headline',
            '',
            '<div class="card summary"><div class="card-body">',
            'this is my summary',
            '</div></div>',
            '',
            'some text'
        ])
    def test_summary_format_epub(self):
        res = self._run_filter(target_format='epub')
        self.assertEqual(MetadataFilter.summary, 'this is my summary')
        self.assertEqual(res, [
            '# my headline',
            '',
            '<p class="summary">',
            'this is my summary',
            '</p>',
            '',
            'some text'
        ])
    def test_summary_format_latex(self):
        res = self._run_filter(target_format='latex')
        self.assertEqual(MetadataFilter.summary, 'this is my summary')
        self.assertEqual(res, [
            '# my headline',
            '',
            '**this is my summary**',
            '',
            'some text'
        ])
    def test_summary_format_none(self):
        res = self._run_filter(target_format=None)
        self.assertEqual(MetadataFilter.summary, 'this is my summary')
        self.assertEqual(res, [
            '# my headline',
            '',
            'this is my summary',
            '',
            'some text'
        ])

    def test_no_header(self):
        pass  # TODO


class TestMetadataFilterMetadata(TestMetadataFilter):

    def setUp(self):

        self.input = [
            '[:author]: # "John Doe"',
            '[:menu-title]: # "a shorter title"',
            '',
            '# my headline',
            '',
            '<summary>',
            'this is my summary',
            '</summary>',
            '',
            'some text']

    def test_metadata_extraction(self):
        self._run_filter()

        self.assertEqual(MetadataFilter.title, 'my headline')
        self.assertEqual(MetadataFilter.summary, 'this is my summary')
        print(repr(MetadataFilter.metadata))
        self.assertEqual(MetadataFilter.metadata['author'], 'John Doe')
        self.assertEqual(MetadataFilter.metadata['menu-title'], 'a shorter title')

    def test_metadata_removal(self):
        """Metadata is removed from file."""
        res = self._run_filter(target_format=None)

        self.assertEqual(res, [
            '# my headline',
            '',
            'this is my summary',
            '',
            'some text'
        ])

