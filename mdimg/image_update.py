# -*- coding: utf-8 -*-

"""
Update image references in multimarkdown files (and preserve deckset formatting).

TODO: refactor so the tool adds error markup and variants inline {++![](variant1)++}} and {-- --} around original

"""

from __future__ import print_function
from __future__ import absolute_import

import logging
import os
import os.path
import re
import shutil
import sys


from .common import filter_dirs, DOCUMENT_TYPES
from .image_repo import ImageRepo


# TODO: add command to parse for unknown image references and list errors only
# TODO: add command to check for unresolved critic markup with image reference errors


def check_images_cmd(args):
    """List images and check for duplicate names."""
    image_repo = ImageRepo(args.image_root)
    image_repo.check_duplicates()


def update_images_cmd(args):
    print('building image repository...')
    image_repo = ImageRepo(args.image_root)

    image_repo.check_duplicates()
    print('processing documents...')
    p = DocumentProcessor(image_repo, args)
    p.list()
    p.run()

    image_repo.report_usage()
    image_repo.report_missing_images()


class DocumentProcessor(object):

    def __init__(self, image_repo, args):
        self.image_repo = image_repo
        self.root = args.document_root
        self.commit = args.commit
        self.keep_backup = args.keep_backup

        self.documents = []
        self._find_documents()

    def _find_documents(self):
        for root, dirs, files in os.walk(self.root):
            filter_dirs(dirs)
            for doc in files:
                _name, ext = os.path.splitext(doc)
                if ext.lower() in DOCUMENT_TYPES:
                    self.documents.append(os.path.join(root, doc))

    def list(self):
        """List all documents."""
        for doc in self.documents:
            logging.info(doc)

    def run(self):
        """Process all documents."""

        for doc in self.documents:
            d = Document(doc, self.image_repo, self.commit, self.keep_backup)
            d.process()


class Document(object):

    ERROR_OUT = sys.stderr

    def __init__(self, path, image_repo, commit, keep_backup):
        self.path = path
        self.image_repo = image_repo
        self.commit = commit
        self.keep_backup = keep_backup
        self.document_has_errors = False

    def process(self):
        print("processing file", self.path, '...')

        if self.commit:
            target_path = self.path + '.updated'
            original = self.path
            print('original', original)
            print('target', target_path)
            with file(original, 'r') as source:
                with file(target_path, 'w+') as target:
                    self.parse_file(source, target.write)

            if self.keep_backup:
                shutil.move(original, self.path + '.backup')
            else:
                os.unlink(original)

            if self.document_has_errors:
                # keep prefix target with '--''
                shutil.move(target_path, os.path.join(os.path.dirname(self.path),
                                                      '--' + os.path.basename(self.path)))
            else:
                shutil.move(target_path, self.path)
        else:
            with file(self.path, 'r') as source:
                def ignore(s):
                    pass
                self.parse_file(source, ignore)

    def parse_file(self, source, writer):
        def _update_image_ref(m):
            image_path = m.group(2)
            self.image_repo.count_usage(image_path)
            return m.group(1) + self.image_repo.translate_path(image_path) + m.group(3)

        line_number = 0
        while True:
            line_number += 1
            line = source.readline()
            if line == '':
                break
            try:
                result = re.sub(r"(.*?\!\[.*?\]\()(.*?)(\).*)", _update_image_ref, line)
                if line != result:
                    logging.debug(':: %s' % line.strip())
                    logging.debug('>> %s' % result.strip())
                writer(result)

            except ImageRepo.ImageNotFoundException as e:
                self.document_has_errors = True
                print(e.message(self.path, line_number), file=self.ERROR_OUT)
                writer('{>>ERROR--image reference not found:<<}\n')
                writer(line)

            except ImageRepo.DuplicateImageException as e:
                self.document_has_errors = True
                print(e.message(self.path, line_number), file=self.ERROR_OUT)
                writer('{>>ERROR--ambiguous image reference:<<}\n')
                for idx, variant in enumerate(e[1]):
                    writer('{>>variant ' + str(idx) + ':<<}\n')
                    writer(line.replace(e[0], variant))
                writer('{>>original reference:<<}\n')
                writer(line)
