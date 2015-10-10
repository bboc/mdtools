# -*- coding: utf-8 -*-

import unittest
import os
from image_update import run_cmd
import tempfile
import filecmp


def test_dir():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                        'test-data')    

def make_path(file_name):
    return os.path.join(test_dir(), file_name)


class BasicImageUpdateTests(unittest.TestCase):

    def setUp(self):
        """Create temp folder, copy test case data."""
        self.document_root = tempfile.mkdtemp()
        self.image_root = os.path.join(test_dir(), 'img')

        # remove temp folder
        self.addCleanup(shutil.rmtree, self.document_root)

    def compare_results(self, result_file, correct_file):
        """Compare the actual result with the correct result."""
        with file(correct_file, 'r+') as correct:
            c = correct.readlines()
            with file(result_file, 'r+') as result
            r = result.readlines()
            self.assertEqual(c, t)

    def compare_files(self, a,b):
        self.assertTrue(filecmp.cmp(a, b, shallow=False])

    def test_one(self):
        self.fail()

        