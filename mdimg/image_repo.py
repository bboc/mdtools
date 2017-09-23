# -*- coding: utf-8 -*-

from __future__ import print_function


import os
import os.path
from collections import defaultdict
from textwrap import dedent

from common import VerbosityControlled, LEVEL_1, LEVEL_2, IMAGE_TYPES

from common import filter_dirs


class ImageRepo(VerbosityControlled):

    def __init__(self, root, verbosity):
        """
        root: path to the folder that contains the images
        """
        self.root = os.path.abspath(root)
        self.verbosity = verbosity
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
        root, dirs, files = os.walk(self.root).next()
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
                self.vprint(LEVEL_2, '...processing', path_prefix)
                for image in files:
                    _name, ext = os.path.splitext(image)
                    if ext.lower() in IMAGE_TYPES:
                        image_ref = os.path.join(path_prefix, image)
                        self.vprint(LEVEL_1, image_ref)
                        self.images[language][image].append(os.path.join(self.relative_root, image_ref))
                        self.usage_counter[language][image] = 0

    def check_duplicates(self):
        """Check repo for duplicate image names."""
        for key in self.images.keys():
            if len(self.images[key]) > 1:
                self.vprint(LEVEL_1, '::duplicate image name:', key, repr(self.images[key]))

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
        print('-' * 19)
        print('--- Images Used ---')
        print('-' * 19)

        def _count(x):
            return x[1]
            for language in self.languages:
                for (img, count) in sorted(self.usage_counter[language].items(), key=_count):
                    try:
                        print(self.images[language][img][0], count)
                    except IndexError:
                        print(img, count)

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
                for image_path in sorted(self.missing_counter[language].keys()):
                    print(image_path, self.missing_counter[language][image_path])
                else:
                    print("--all images in language '%s' were replaced, no images missing--" % (language))
