# -*- coding: utf-8 -*-

import unittest

from mdbuild import markdown_processor as mdp


class TestMetadataFilter(unittest.TestCase):

    def _run_filter(self, strip_summary_tags=False):
        return [line for line in mdp.MetadataPlugin.filter(iter(self.input), strip_summary_tags=strip_summary_tags)]


class TestMetadataFilterBasics(TestMetadataFilter):

    def test_empty_file(self):
        self.input = []
        res = self._run_filter()
        self.assertEqual(res, [])

    def setUp(self):

        self.input = [
            '# my headline',
            '',
            '<summary>',
            'this is my summary',
            '</summary>',
            '',
            'some text']

    def test_title_and_summary(self):
        """Title and summary are extracted properly."""
        self._run_filter()
        self.assertEqual(mdp.MetadataPlugin.title, 'my headline')
        self.assertEqual(mdp.MetadataPlugin.summary, 'this is my summary')

        # if summary is enclosed in **, markup is removed properly
        self.input[3] = '**this is my summary**'
        res = self._run_filter()
        self.assertEqual(mdp.MetadataPlugin.summary, 'this is my summary')
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
        self.assertEqual(mdp.MetadataPlugin.summary, 'this is my summary')
        self.assertEqual(res, [
            '# my headline',
            '',
            'this is my summary',
            '',
            'some text'
            ])


