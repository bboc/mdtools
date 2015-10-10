# -*- coding: utf-8 -*-

import unittest
import os
import shutil
from image_update import run_cmd, get_parser
import tempfile
import filecmp


def test_dir():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                        'test-data')    

def make_path(*args):
    return os.path.join(test_dir(), *args)


class BasicImageUpdateTests(unittest.TestCase):

    def setUp(self):
        """Create temp folder, copy test case data."""
        self.maxDiff = None
        self.document_root = tempfile.mkdtemp()
        self.image_root = test_dir()

        print(self.document_root)
        # TODO: remove temp folder
        # self.addCleanup(shutil.rmtree, self.document_root)

    def compare_results(self, result_file, correct_file):
        """Compare the actual result with the correct result."""
        with file(correct_file, 'r+') as correct:
            c = correct.readlines()
            with file(result_file, 'r+') as result:
                r = result.readlines()
                self.assertEqual(c, r)

    def compare_files(self, a,b):
        self.assertTrue(filecmp.cmp(a, b, shallow=False))

    def test_one(self):

        # copy testcase full-test to tempfolder
        shutil.copytree(make_path('testcases', 'full-test', 'documents'), 
                        os.path.join(self.document_root, 'documents')) 
        parser = get_parser()
        args = parser.parse_args(['run', self.document_root, '-i', self.image_root, '--commit', '--keep'])
        run_cmd(args)

        # compare test results with correct files
        self.compare_results(make_path('testcases', 'full-test', 'results', 'document_one.txt'),
                             os.path.join(self.document_root, 'documents', 'document_one.txt'))
        self.compare_results(make_path('testcases', 'full-test', 'results', 'document_two.mmd'),
                             os.path.join(self.document_root, 'documents', 'subfolder', 'document_two.mmd'))

        # TODO: check backup files to original files
        self.compare_results(make_path('testcases', 'full-test', 'documents', 'document_one.txt'),
                             os.path.join(self.document_root, 'documents', 'document_one.txt.backup'))
        self.compare_results(make_path('testcases', 'full-test', 'documents', 'subfolder', 'document_two.mmd'),
                             os.path.join(self.document_root, 'documents', 'subfolder', 'document_two.mmd.backup'))

        self.compare()

        self.fail()

