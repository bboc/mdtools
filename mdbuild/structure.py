# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import absolute_import

import codecs
from functools import partial
import logging
import os

from .common import read_config_file, FILENAME_PATTERN, disable_exception_traceback
from . import glossary
from . import macros
from .renderer import Renderer, filters

logger = logging.getLogger(__name__)

# the document structure
structure = None


def set_structure(filename, content_path):
    logger.info("-- reading structure '%s'" % filename)

    macros.register_macro('glossary', glossary.glossary_term_macro)
    macros.register_macro('define', glossary.glossary_definition_macro)

    cs = ContentRoot.from_config(read_config_file(filename))
    cs.read_info(content_path)
    # logger.debug(cs.to_dict())
    globals()['structure'] = cs


class ContentNode(object):
    """
    The main content object consists of nested ContentNodes.

    Each ContentNode has:
    - root (the content object)
    - parent
    - slug (the bit that is listed in the structure.yaml
    - id (full path from root)
    - title extracted from file
    - parameters (extracted from structure yaml)
    - tags (part of parameters??)
    """

    def __init__(self, slug, parent, root, level):
        pass
        self.slug = slug
        self.parent = parent
        self.root = root
        self.level = level
        self.parts = []
        self.title = ''
        self.nav_title = ''
        self.config = {}
        self.tags = []
        self.summary = ''
        self.metadata = {}

    def is_root(self):
        return self is self.root

    @property
    def id(self):
        return '.'.join((self.parent.id, self.slug))

    @property
    def path(self):
        return os.path.join(self.parent.path, self.slug)

    @property
    def relpath(self):
        return os.path.join(self.parent.relpath, self.slug)

    @property
    def source_path(self):
        """
        Return the actual source path for the content file.

        - <path>.md
        - <path>/index.md
        - <path>/<slug>.md
        """
        source_path = self.md_filename(self.path)
        if os.path.exists(source_path):
            return source_path
        elif self.parts:
            for source_path in [
                self.md_filename(os.path.join(self.path, 'index')),
                self.md_filename(os.path.join(self.path, self.slug)),
                self.md_filename(os.path.join(self.path, '_'.join((self.slug, 'index'))))
            ]:
                if os.path.exists(source_path):
                    return source_path
            with disable_exception_traceback():
                raise Exception('Source file "%s" not found' % source_path)
        else:
            with disable_exception_traceback():
                raise Exception('Source file "%s" not found' % source_path)

        return source_path

    @property
    def last_descendant(self):
        """
        Return the last descendant of the current node  (recursive).
        If the current node has no parts, it's its own last descendant
        """
        if self.parts:
            return self.parts[-1].last_descendant
        else:
            return self

    @property
    def predecessor(self):
        """
        Return the object that precedes this one when reading end-to-end:
        - the last descendant of previous sibling (which might be the previous sibling itself)
        - the parent, or None.
        """
        idx = self.parent.parts.index(self)
        if idx:  # there is a previous sibling
            return self.parent.parts[idx - 1].last_descendant
        elif not self.parent.is_root():
            return self.parent
        else:
            return None

    @property
    def next_sibling_or_ancestor_sibling(self):
        """If the node has next sibling:
        """
        idx = self.parent.parts.index(self)
        if idx + 1 < len(self.parent.parts):
            # there is a next sibling
            return self.parent.parts[idx + 1]
        elif not self.parent.is_root():
            return self.parent.next_sibling_or_ancestor_sibling
        else:
            return None

    @property
    def successor(self):
        """
        Return the object that succedes this one when reading end-to-end:
        - the first child
        - the next sibling, or the next sibling of the closest ancestor,
          (which might be None)
        """
        if self.parts:
            return self.parts[0]
        else:
            return self.next_sibling_or_ancestor_sibling

    def md_filename(self, fn):
        return FILENAME_PATTERN % fn

    def to_dict(self):
        d = {
            'id': self.id,
            'class': self.__class__,
            'slug': self.slug,
            'summary': self.summary,
            'title': self.title,
            'path': self.path,
        }
        if self.parts:
            d['parts'] = [p.to_dict() for p in self.parts]
        if self.tags:
            d['tags'] = self.tags
        if self.config:
            d['config'] = repr(self.config)
        if self.metadata:
            d['metadata'] = self.metadata

        return d

    @classmethod
    def from_config(cls, data, parent, root, level):
        logger.debug(data)
        if data.__class__ == dict:
            item = cls(data['id'], parent, root, level)
            if 'tags' in data:
                item.tags = data['tags']
            if 'config' in data:
                item.config = data['config']
            if 'parts' in data:
                item.parts = [ContentNode.from_config(part, item, parent, level + 1) for part in data['parts']]
        else:
            item = cls(data, parent, root, level)

        return item

    def read_info(self):
        """Read info from content file."""
        self._read_info()

        for part in self.parts:
            part.read_info()

    def _read_info(self):
        """Extract titles, summaries and medatada from a node's content."""
        if not os.path.exists(self.source_path):
            raise Exception("ERROR: source_path %s doesn't exist)" % self.path)
        with codecs.open(self.source_path, 'r', 'utf-8') as source:
            renderer = Renderer(source, filters=[
                partial(macros.MacroFilter.filter, ignore_unknown=True),
                filters.MetadataFilter.filter,
            ])
            renderer.render()
            logger.debug("node title: '%s'" % filters.MetadataFilter.title)
            self.title = filters.MetadataFilter.title
            self.summary = filters.MetadataFilter.summary
            self.metadata = filters.MetadataFilter.metadata

    def find(self, slug):
        """Find slug in this subtree"""
        if self.slug == slug:
            return self
        for part in self.parts:
            res = part.find(slug)
            if res:
                return res
        else:
            return None


class ContentRoot(ContentNode):
    """
    A representation of the entire content.

    Content is split into parts, which can havbe parts again, ad infinitum (in practcie, there's only a limited number
    of header levels in most output formats).
    """
    def __init__(self, root_path):
        self.root_path = root_path
        super(ContentRoot, self).__init__(None, None, self, 0)

    @classmethod
    def from_config(cls, structure, path=None):
        c = cls(path)
        c.root_path = path
        c.config = structure['config']
        c.parts = [ContentNode.from_config(part, c, c, 1) for part in structure['parts']]
        return c

    def to_dict(self):
        return {
            'config': self.config,
            'parts': [p.to_dict() for p in self.parts],
        }

    def read_info(self, content_path):
        """Read titles and structure etc. from content files."""
        self.root_path = content_path
        for part in self.parts:
            part.read_info()

    @property
    def id(self):
        return ''

    @property
    def path(self):
        return self.root_path

    @property
    def relpath(self):
        return ''

    @property
    def predecessor(self):
        return None

    @property
    def next_sibling_or_ancestor_sibling(self):
        return None

    @property
    def successor(self):
        """
        Return the object that succedes this one when reading end-to-end:
        - the first child
        - the next sibling, or the next sibling of the closest ancestor,
          (which might be None)
        """
        if self.parts:
            return self.parts[0]
        else:
            return self.next_sibling_or_ancestor_sibling
