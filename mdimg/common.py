# -*- coding: utf-8 -*-

from __future__ import print_function

IMAGE_TYPES = ['.png', '.gif', '.jpg', '.jpeg']
DOCUMENT_TYPES = ['.txt', '.md', '.mmd', '.markdown', '.multimarkdown']
EXCLUDE_DIRS = ['.git', 'CVS', 'SVN']
LEVEL_0 = 0
LEVEL_1 = 1
LEVEL_2 = 2
LEVEL_3 = 3


def filter_dirs(dirs):
    for item in dirs:
        if item in EXCLUDE_DIRS:
            dirs.remove(item)


class VerbosityControlled(object):
    """Mixin for filtered printing."""
    def vprint(self, level, *args, **kwargs):
        if level <= self.verbosity:
            print(*args, **kwargs)
