# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import absolute_import

import logging
import os
import os.path
from collections import defaultdict
from textwrap import dedent

from .common import IMAGE_TYPES

from .common import filter_dirs


class ImageRepo(object):

    def __init__(self, root):
        """
        root: path to the folder that contains the images
        """
        self.root = os.path.abspath(root)
        self.relative_root = os.path.split(root)[1]
        self.languages = []

        self.images = defaultdict(lambda: defaultdict(list))
        self.usage_counter = defaultdict(lambda: defaultdict(int))
        self.missing_counter = defaultdict(lambda: defaultdict(int))

        self.languages = self._find_languages()
        self._build_repo_structure()

    class DuplicateImageException(Exception):
        def message(self, path, line_number):
            return dedent("""
                ambiguous image reference in "{}", line {}:
                "{}" --> "{}" """).format(path, line_number, self[0], repr(self[1]))

    class ImageNotFoundException(Exception):
        def message(self, path, line_number):
            return dedent("""
                image not found in file "{}", line {}:
                image reference: "{}" """).format(path, line_number, self[0])

    def _find_languages(self):
        # TODO: there must be a better way than using os.walk this way?
        root, dirs, files = next(os.walk(self.root))
        filter_dirs(dirs)
        return dirs

    def _build_repo_structure(self):
        """
        Walk the filesystem and add all images to repository.
        Set imagecout to 0 for each image.
        """
        for language in self.languages:
            lang_root = os.path.join(self.root, language)
            for root, dirs, files in os.walk(lang_root):
                dirs = filter_dirs(dirs)
                path_prefix = root[len(self.root) + 1:]
                logging.debug('...processing %s' % path_prefix)
                for image in files:
                    _name, ext = os.path.splitext(image)
                    if ext.lower() in IMAGE_TYPES:
                        image_ref = os.path.join(path_prefix, image)
                        logging.debug(image_ref)
                        self.images[language][image].append(os.path.join(self.relative_root, image_ref))
                        self.usage_counter[language][image] = 0

    def check_duplicates(self):
        """Check repo for duplicate image names."""
        for language in self.languages:
            has_duplicate = False
            logging.warning("\n--- duplicates [%s]---" % language)
            for image in sorted(self.images[language].keys()):
                if len(self.images[language][image]) > 1:
                    has_duplicate = True
                    logging.warning("\n::: %s" % image)
                    for version in self.images[language][image]:
                        logging.warning("    %s" % version)
            if not has_duplicate:
                logging.warning("\n    no duplicates found\n")

    def _get_lang_and_image(self, image_path):
        parts = []
        tail = True
        while tail:
            image_path, tail = os.path.split(image_path)
            parts.append(tail)
        return parts[-3], parts[0]

    def translate_path(self, old_image_path):
        """Identify and return new image path."""
        if os.path.exists(os.path.join(os.path.split(self.root)[0], old_image_path)):
            # no need to do anything if old image still exists!
            return old_image_path

        language, image_name = self._get_lang_and_image(old_image_path)
        if image_name in self.images[language]:
            if len(self.images[language][image_name]) == 1:
                return self.images[language][image_name][0]
            else:
                raise self.DuplicateImageException(old_image_path, self.images[language][image_name])
        else:
            self.count_missing(old_image_path)
            raise self.ImageNotFoundException(old_image_path, image_name)

    def count_usage(self, image_path):
        language, image_name = self._get_lang_and_image(image_path)
        self.usage_counter[language][image_name] += 1

    def report_usage(self):
        logging.info('-' * 19)
        logging.info('--- Images Used ---')
        logging.info('-' * 19)

        def _count(x):
            return x[1]
            for language in self.languages:
                for (img, count) in sorted(self.usage_counter[language].items(), key=_count):
                    try:
                        logging.info("%s (%s)" % (self.images[language][img][0], count))
                    except IndexError:
                        logging.info("%s (%s)" % (img, count))

    def count_missing(self, image_path):
        language, image_name = self._get_lang_and_image(image_path)
        self.missing_counter[language][image_name] += 1

    def report_missing_images(self):
        if len(self.missing_counter):
            print('-' * 22)
            print('--- Missing Images ---')
            print('-' * 22)
            for language in self.languages:
                print("--- language:", language)
                if self.missing_counter[language].keys():
                    for image_path in sorted(self.missing_counter[language].keys()):
                        print(image_path, self.missing_counter[language][image_path])
                else:
                    print("--all images in language '%s' were replaced, no images missing--" % (language))
