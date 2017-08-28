# -*- coding: utf-8 -*-

import filecmp
from mdimg.image_update import update_images_cmd, Document
from mdimg.command import get_parser
import os
import shutil
import sys
import tempfile
import unittest


def data_dir():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        'test-data')


def make_path(*args):
    return os.path.join(data_dir(), *args)


class BasicImageUpdateTests(unittest.TestCase):

    def setUp(self):
        """Create temp folder, copy test case data."""
        self.maxDiff = None
        self.document_root = tempfile.mkdtemp()
        self.image_root = data_dir()
        self.addCleanup(shutil.rmtree, self.document_root)
        self.parser = get_parser()
        # suppress error out
        Document.ERROR_OUT = sys.stdout

    def compare_results(self, result_file, correct_file):
        """Compare the actual result with the correct result."""
        with file(correct_file, 'r+') as correct:
            c = correct.readlines()
            with file(result_file, 'r+') as result:
                r = result.readlines()
                self.assertEqual(c, r)

    def compare_files(self, a, b):
        self.assertTrue(filecmp.cmp(a, b, shallow=False))

    def create_fixture(self, *args):
        """Copy testcase to tempfolder."""
        shutil.copytree(make_path('testcases', *args),
                        os.path.join(self.document_root, 'documents'))

    def _validate_tc1_documents(self):
        self.compare_results(make_path('testcases', 'full-test', 'results', 'document_one.txt'),
                             os.path.join(self.document_root, 'documents', '--document_one.txt'))
        self.assertFalse(os.path.exists(os.path.join(self.document_root, 'documents', 'document_one.txt')))
        self.compare_results(make_path('testcases', 'full-test', 'results', 'document_two.mmd'),
                             os.path.join(self.document_root, 'documents', 'subfolder', 'document_two.mmd'))
        self.compare_results(make_path('testcases', 'full-test', 'documents', 'document_three.md'),
                             os.path.join(self.document_root, 'documents', 'document_three.md'))

    def test_update_images_with_commit(self):
        self.create_fixture('full-test', 'documents')
        args = self.parser.parse_args(['update-images', self.document_root, '-i', self.image_root, '--commit'])
        update_images_cmd(args)

        # make sure document contens are valid
        self._validate_tc1_documents()

        # make sure backups don't exist
        self.assertFalse(os.path.exists(os.path.join(self.document_root, 'documents', 'document_one.txt.backup')))
        self.assertFalse(os.path.exists(os.path.join(self.document_root, 'documents', 'subfolder', 'document_two.mmd.backup')))
        self.assertFalse(os.path.exists(os.path.join(self.document_root, 'documents', 'document_three.md.backup')))

    def test_update_images_with_commit_and_keep_backups(self):

        self.create_fixture('full-test', 'documents')
        args = self.parser.parse_args(['update-images', self.document_root, '-i', self.image_root, '--commit', '--keep'])
        update_images_cmd(args)

        # make sure document contens are valid
        self._validate_tc1_documents()

        # test for backup files
        self.compare_results(make_path('testcases', 'full-test', 'documents', 'document_one.txt'),
                             os.path.join(self.document_root, 'documents', 'document_one.txt.backup'))
        self.compare_results(make_path('testcases', 'full-test', 'documents', 'subfolder', 'document_two.mmd'),
                             os.path.join(self.document_root, 'documents', 'subfolder', 'document_two.mmd.backup'))
        self.compare_results(make_path('testcases', 'full-test', 'documents', 'document_three.md'),
                             os.path.join(self.document_root, 'documents', 'document_three.md.backup'))
