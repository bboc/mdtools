# -*- coding: utf-8 -*-
"""
Helpers for tests
"""

import filecmp
import shutil
import tempfile
import unittest


class FileBasedTestCase(unittest.TestCase):

    def setUp(self):
        """Create temp folder, copy test case data."""
        self.document_root = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.document_root)

    def compare_results(self, result_file, correct_file):
        """Compare the actual result with the correct result."""
        with file(correct_file, 'r+') as correct:
            c = correct.readlines()
            with file(result_file, 'r+') as result:
                r = result.readlines()
                self.assertEqual(c, r)

    def compare_files(self, a, b):
        self.assertTrue(filecmp.cmp(a, b, shallow=False))
