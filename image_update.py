# -*- coding: utf-8 -*-

"""
transclude multimarkdown files.
"""

from __future__ import print_function

import os
import os.path
from collections import defaultdict

IMAGE_TYPES = ['.png', '.gif', '.jpg', '.jpeg']
DOCUMENT_TYPES = ['.txt', '.md', '.mmd', '.markdown', '.multimarkdown']
EXCLUDE_DIRS = ['.git', 'CVS', 'SVN']

def image_update(document_root, image_root):
    if not os.path.exists(document_root):
        raise MissingDocumentRootException(document_root)
    if not os.path.exists(image_root):
        raise MissingImageRootException(image_root)

    image_repo = ImageRepo(image_root)

    image_repo.check_duplicates()

    process_documents(document_root, image_repo)


class ImageRepo(object):

    def __init__(self, root):
        self.root = root
        self.images = defaultdict(list)
        self._build_repo_structure()

    def _build_repo_structure(self):
        for root, dirs, files in os.walk(self.root):
            dirs = filter_dirs(dirs)
            path_prefix = root[len(self.root):]
            print('-------processing', path_prefix)
            for image in files:
                _name, ext = os.path.splitext(image)
                if ext.lower() in IMAGE_TYPES:
                    self.images[image].append('/'.join((path_prefix, image)))

    
    def check_duplicates(self):
        for key in self.images.keys():
            if len(self.images[key]) > 1:
                print('::duplicate image:', key, repr(self.images[key]))


def process_documents(document_root, image_repo):
    for root, dirs, files in os.walk(document_root):
        filter_dirs(dirs)
        for doc in files:
            _name, ext = os.path.splitext(doc)
            if ext.lower() in DOCUMENT_TYPES:
                update_document(os.path.join(root, doc), image_repo)

def update_document(doc, repo):
    pass

def filter_dirs(dirs):
    for item in dirs:
        if item in EXCLUDE_DIRS:
            dirs.remove(item)


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

    args = parser.parse_args()
    try:
        image_update(args.document_root, args.image_root)
    except MissingDocumentRootException, e:
        print('ERROR: missing document root:', e[0], file=sys.stderr)
        sys.exit(1)
    except MissingImageRootException, e:
        print ('ERROR: missing image root', e[0], file=sys.stderr)
        sys.exit(2)


if __name__ == '__main__':
    main()


