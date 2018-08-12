# -*- coding: utf-8 -*-
"""
Tests for mdimg, language specific.

Test case structure

img/ba contains the actual tests, with duplicate files, and files that are moved.
img/fo contains a couple of images which are also in img/ba, but they are referenced correctly

also there's needs to be an additional test that makes probes the image memory for languages 'fo' and 'ba'.

In addition to that, images in the root must also be processed correctly, or responded
to with an error!
"""

import filecmp
import os
import shutil
import sys

from tests.common import FileBasedTestCase

from mdimg.image_update import update_images_cmd, Document, ImageRepo
from mdimg.command import get_parser


def data_dir():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        'test-data')


def make_path(*args):
    return os.path.join(data_dir(), *args)


class ImageTestBase(FileBasedTestCase):

    def setUp(self):
        """Create temp folder, copy test case data."""
        super(ImageTestBase, self).setUp()
        self.maxDiff = None
        self.image_root = os.path.join(data_dir(), 'img')
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


class ImageUpdateTests(ImageTestBase):

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


class ImageRepositoryTests(ImageTestBase):
    # nosetests tests/image_update_tests.py:ImageRepositoryTests

    def setup_image_repo(self):
        self.create_fixture('full-test', 'documents')
        args = self.parser.parse_args(['update-images', self.document_root, '-i', self.image_root])
        return ImageRepo(args.image_root)

    def test_probe_image_repository(self):
        """
        Make sure image repo is populated correctly, and usage_counter is zero for all
        """
        image_repo = self.setup_image_repo()
        # relative root is recognized:
        self.assertEqual(image_repo.relative_root, 'img')
        # languages are detected
        self.assertEqual(sorted(image_repo.languages), ['ba', 'fo'])
        # image repo has languages at it's root
        self.assertEqual(sorted(image_repo.images), ['ba', 'fo'])
        # images are added and duplicateds are listed with correct paths
        self.assertEqual(sorted(image_repo.images['ba']['image.gif']), ['img/ba/duplicate/image.gif', 'img/ba/image.gif'])
        self.assertEqual(image_repo.usage_counter['ba']['image.gif'], 0)

    def test_tranlsate_path_for_unchanged_image(self):
        image_repo = self.setup_image_repo()
        self.assertEqual(image_repo.translate_path('img/fo/fo-only.jpg'), 'img/fo/fo-only.jpg')

    def test_translate_path_with_language(self):
        image_repo = self.setup_image_repo()
        self.assertEqual(image_repo.translate_path('img/ba/oldfolder/other/ba-only.jpg'), 'img/ba/ba-only.jpg')

    def test_translate_raises_duplicate_image_exception(self):
        image_repo = self.setup_image_repo()
        self.assertRaises(ImageRepo.DuplicateImageException, image_repo.translate_path, 'img/ba/none/image.gif')

    def test_image_unknown_in_language_raises_exception(self):
        image_repo = self.setup_image_repo()
        # image present in one language:
        self.assertEqual(image_repo.translate_path('img/fo/fo-only.jpg'), 'img/fo/fo-only.jpg')
        # but missing in another:
        self.assertRaises(ImageRepo.ImageNotFoundException, image_repo.translate_path, 'img/ba/fo-only.jpg')

    def test_count_and_report_missing(self):
        image_repo = self.setup_image_repo()
        # image present in one language:
        image_repo.count_missing('img/fo/image.gif')
        self.assertEqual(image_repo.missing_counter['ba']['image.gif'], 0)
        self.assertEqual(image_repo.missing_counter['fo']['image.gif'], 1)
        image_repo.report_missing_images()

    def test_count_and_report_usage(self):
        image_repo = self.setup_image_repo()
        # image present in one language:
        image_repo.count_usage('img/fo/image.gif')
        self.assertEqual(image_repo.usage_counter['ba']['image.gif'], 0)
        self.assertEqual(image_repo.usage_counter['fo']['image.gif'], 1)
        image_repo.report_usage()


