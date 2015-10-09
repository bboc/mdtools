# -*- coding: utf-8 -*-

"""
update image references in multimarkdown files (and preserve deckset formatting.
"""

from __future__ import print_function

import os
import os.path
import re
import sys
from collections import defaultdict
from textwrap import dedent

IMAGE_TYPES = ['.png', '.gif', '.jpg', '.jpeg']
DOCUMENT_TYPES = ['.txt', '.md', '.mmd', '.markdown', '.multimarkdown']
EXCLUDE_DIRS = ['.git', 'CVS', 'SVN']
LEVEL_1 = 1
LEVEL_2 = 2
LEVEL_3 = 3 

def image_update(document_root, image_root, image_prefix, verbosity):
    print("verbosity", verbosity)
    if not os.path.exists(document_root):
        raise MissingDocumentRootException(document_root)
    if not os.path.exists(image_root):
        raise MissingImageRootException(image_root)

    print('building image repo...')
    image_repo = ImageRepo(image_root, image_prefix, verbosity)

    image_repo.check_duplicates()

    print('processing documents...')
    p = DocumentProcessor(document_root, image_repo, verbosity)

    p.list()
    #process_documents(document_root, image_repo)
    p.run()


def filter_dirs(dirs):
    for item in dirs:
        if item in EXCLUDE_DIRS:
            dirs.remove(item)


class VerbosityControlled(object):
    """Mixin for filtered printing."""
    def vprint(self, level, *args, **kwargs):
        if level <= self.verbosity:
            print(*args, **kwargs)


class ImageRepo(VerbosityControlled):

    class DuplicateImageException(Exception):
        pass

    class ImageNotFoundException(Exception):
        pass

    def __init__(self, root, path_prefix, verbosity):
        self.root = root
        self.path_prefix = path_prefix
        self.verbosity = verbosity
        self.images = defaultdict(list)
        self._build_repo_structure()

    def _build_repo_structure(self):
        for root, dirs, files in os.walk(self.root):
            dirs = filter_dirs(dirs)
            path_prefix = root[len(self.root):]
            self.vprint(LEVEL_2, '...processing', path_prefix)
            for image in files:
                _name, ext = os.path.splitext(image)
                if ext.lower() in IMAGE_TYPES:
                    self.images[image].append(os.path.join(path_prefix, image))

    
    def check_duplicates(self):
        for key in self.images.keys():
            if len(self.images[key]) > 1:
                self.vprint(LEVEL_2, '::duplicate image:', key, repr(self.images[key]))

    def translate_path(self, old_image_path):
        dummy, image = os.path.split(old_image_path)
        if self.images.has_key(image):
            if len(self.images[image]) == 1:
                return os.path.join(self.path_prefix, self.images[image][0])
            else:
                 raise self.DuplicateImageException(old_image_path, self.images[image])
        else:
            raise self.ImageNotFoundException(old_image_path, image)


class DocumentProcessor(VerbosityControlled):

    def __init__(self, root, image_repo, verbosity):
        self.root = root
        self.image_repo = image_repo
        self.verbosity = verbosity

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
            self.vprint(LEVEL_2, doc)

    def run(self):
        """Process all documents."""

        for doc in self.documents:
            d = Document(doc, self.image_repo, self.verbosity)
            d.process()


class Document(VerbosityControlled):

    def __init__(self, path, image_repo, verbosity):
        self.path = path
        self.image_repo = image_repo
        self.verbosity = verbosity


    def process(self):

        def repl(m):
            image_path = m.group(2)
            return m.group(1) + self.image_repo.translate_path(image_path) + m.group(3)


        with file(self.path, 'r') as source:
            line_number = 0
            while True:
                line_number += 1
                line = source.readline()
                if line == '':
                    break
                try:
                    result = re.sub(r"(.*?\!\[.*?\]\()(.*)(\).*)", repl, line)

                except ImageRepo.ImageNotFoundException, e:
                    print(dedent("""
                        ------------------------
                        :::IMAGE REFERENCE NOT ImageNotFoundException
                        file "{}", line {}:
                        image reference: "{}"
                        possible targets "{}"
                        """).format(self.path, line_number, e[0], repr(e[1])),
                        file=sys.stderr)

                except ImageRepo.DuplicateImageException, e:
                    print(dedent("""
                        ------------------------
                        :::AMBIGUOUS IMAGE REFERENCE
                        file "{}", line {}:
                        image reference: "{}"
                        image repo key: "{}"
                        """).format(self.path, line_number, e[0], repr(e[1])),
                        file=sys.stderr)


class MissingDocumentRootException(Exception):
    pass


class MissingImageRootException(Exception):
    pass


def main():
    import argparse
    import sys
    parser = argparse.ArgumentParser(
        description='update images referenced in source markdown files (.md, .mmd, .txt) to new paths.')
    parser.add_argument('document_root',
                        help='root folder for documents to update')
    parser.add_argument('image_root',
                        help='root folder for new images files')
    parser.add_argument('image_prefix',
                        help='path prefix for new image path')
    parser.add_argument('--verbose', '-v', action='count', default=0)

    args = parser.parse_args()
    try:
        image_update(args.document_root, args.image_root, args.image_prefix, args.verbose)
    except MissingDocumentRootException, e:
        print('ERROR: missing document root:', e[0], file=sys.stderr)
        sys.exit(1)
    except MissingImageRootException, e:
        print ('ERROR: missing image root', e[0], file=sys.stderr)
        sys.exit(2)


if __name__ == '__main__':
    main()

