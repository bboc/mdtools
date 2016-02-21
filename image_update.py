# -*- coding: utf-8 -*-

"""
Update image references in multimarkdown files (and preserve deckset formatting).

TODO: refactor so the tool adds error markup and variants inline {++![](variant1)++}} and {-- --} around original

"""

from __future__ import print_function


import os
import os.path
import re
import shutil
import sys
from collections import defaultdict
from textwrap import dedent

IMAGE_TYPES = ['.png', '.gif', '.jpg', '.jpeg']
DOCUMENT_TYPES = ['.txt', '.md', '.mmd', '.markdown', '.multimarkdown']
EXCLUDE_DIRS = ['.git', 'CVS', 'SVN']
LEVEL_0 = 0
LEVEL_1 = 1
LEVEL_2 = 2
LEVEL_3 = 3 

# TODO: add command to parse for unknown image references and list errors only
# TODO: add command to check for unresolved critic markup with image reference errors

def check_images_cmd(args):
    """List images and check for duplicate names."""
    image_repo = ImageRepo(args.image_root, args.verbose + 1)
    image_repo.check_duplicates()
 

def update_images_cmd(args):
    print("verbosity", args.verbose)
    print('building image repository...')
    image_repo = ImageRepo(args.image_root, args.verbose)

    image_repo.check_duplicates()
    print('processing documents...')
    p = DocumentProcessor(image_repo, args)
    p.list()
    p.run()

    if args.verbose:
        image_repo.report_usage()

    image_repo.report_missing_images()


def list_broken_images_cmd(args):
    print('not implemented yet')


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

    def __init__(self, root, verbosity):
        self.root = root
        self.verbosity = verbosity
        self.images = defaultdict(list)
        self.imagecount = defaultdict(int)
        self.missingcount = defaultdict(int)

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


    def _build_repo_structure(self):
        """Walk the filesystem and add all images to repository."""
        for root, dirs, files in os.walk(self.root):
            dirs = filter_dirs(dirs)
            path_prefix = root[len(self.root)+1:]
            self.vprint(LEVEL_2, '...processing', path_prefix)
            for image in files:
                _name, ext = os.path.splitext(image)
                if ext.lower() in IMAGE_TYPES:
                    image_ref = os.path.join(path_prefix, image)
                    self.vprint(LEVEL_1, image_ref)
                    self.images[image].append(image_ref)
                    self.imagecount[image] = 0
    
    def check_duplicates(self):
        """Check repo for duplicate image names."""
        for key in self.images.keys():
            if len(self.images[key]) > 1:
                self.vprint(LEVEL_1, '::duplicate image name:', key, repr(self.images[key]))

    def translate_path(self, old_image_path):
        """Identify and return new image path."""
        if os.path.exists(os.path.join(self.root, old_image_path)):
            # no need to do anything if old image still exists!
            return old_image_path
        dummy, image_name = os.path.split(old_image_path)
        if self.images.has_key(image_name):
            if len(self.images[image_name]) == 1:
                return self.images[image_name][0]
            else:
                 raise self.DuplicateImageException(old_image_path, self.images[image_name])
        else:
            self.count_missing(old_image_path)
            raise self.ImageNotFoundException(old_image_path, image_name)

    def count_usage(self, image_path):
        dummy, image_name = os.path.split(image_path)
        self.imagecount[image_name] += 1

    def report_usage(self):
        print('-'*19)
        print('--- Images Used ---')
        print('-'*19)
        def _count(x): return x[1]
        for (img, count) in sorted(self.imagecount.items(), key=_count):
            print(img, count)        

    def count_missing(self, image_path):
        self.missingcount[image_path] += 1

    def report_missing_images(self):
        if len(self.missingcount):
            print('-'*22)
            print('--- Missing Images ---')
            print('-'*22)
            def _count(x): return x[1]
            for image_path in sorted(self.missingcount.keys()):
                print(image_path, self.missingcount[image_path])        
        else:
            print("--all images were replaced, no images missing--")


class DocumentProcessor(VerbosityControlled):

    def __init__(self, image_repo, args):
        self.image_repo = image_repo
        self.root = args.document_root
        self.verbosity = args.verbose
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
            self.vprint(LEVEL_2, doc)

    def run(self):
        """Process all documents."""

        for doc in self.documents:
            d = Document(doc, self.image_repo, self.verbosity, self.commit, self.keep_backup)
            d.process()


class Document(VerbosityControlled):

    ERROR_OUT = sys.stderr

    def __init__(self, path, image_repo, verbosity, commit, keep_backup):
        self.path = path
        self.image_repo = image_repo
        self.verbosity = verbosity
        self.commit  = commit
        self.keep_backup = keep_backup
        self.document_has_errors = False


    def process(self):
        self.vprint(LEVEL_0, "processing file", self.path, '...')

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
                result = re.sub(r"(.*?\!\[.*?\]\()(.*)(\).*)", _update_image_ref, line)
                if line != result:
                    self.vprint(LEVEL_3, '::', line.strip())
                    self.vprint(LEVEL_3, '>>', result.strip())
                writer(result)

            except ImageRepo.ImageNotFoundException, e:
                self.document_has_errors = True
                print(e.message(self.path, line_number), file=self.ERROR_OUT)
                writer('{>>ERROR--image reference not found:<<}\n')
                writer(line)
                
            except ImageRepo.DuplicateImageException, e:
                self.document_has_errors = True
                print(e.message(self.path, line_number), file=self.ERROR_OUT)
                writer('{>>ERROR--ambiguous image reference:<<}\n')
                for idx, variant in enumerate(e[1]):
                    writer('{>>variant ' + str(idx) + ':<<}\n')
                    writer(line.replace(e[0], variant))
                writer('{>>original reference:<<}\n')
                writer(line)



