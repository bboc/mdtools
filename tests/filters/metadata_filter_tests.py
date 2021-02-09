# -*- coding: utf-8 -*-

import unittest

from mdbuild.renderer import MetadataFilter


class TestMetadataFilter(unittest.TestCase):

    def _run_filter(self, strip_summary_tags=False):
        return [line for line in MetadataFilter.filter(iter(self.input), strip_summary_tags=strip_summary_tags)]


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
        res = self._run_filter()
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

    def test_strip_summary_tags(self):
        res = self._run_filter(strip_summary_tags=True)
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
        res = self._run_filter(strip_summary_tags=True)

        self.assertEqual(res, [
            '# my headline',
            '',
            'this is my summary',
            '',
            'some text'
        ])

