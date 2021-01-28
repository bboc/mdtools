# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import absolute_import

import codecs
from functools import partial
import logging
import os

from . import markdown_processor as mdp
from .common import read_config_file, FILENAME_PATTERN
from . import glossary
from . import macros

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
    The main content object consists of nested ContentNodes (parts, chapters, sections).

    Each ContentNode has:
    - root (the content object)
    - parent
    - slug (the bit that is listed in the structure.yaml
    - id (full path from root)
    - title extracted from file
    - parameters (extracted from structure yaml)
    - tags (part of parameters??)
    """

    PARTS = 'parts'
    CHAPTERS = 'chapters'
    SECTIONS = 'sections'

    def __init__(self, slug, parent, root):
        pass
        self.parent = parent
        self.root = root
        self.slug = slug
        self.children = []
        self.title = ''
        self.config = {}
        self.tags = []
        self.summary = ''

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
        """Return the actual source path for the content file."""
        source_path = self.md_filename(self.path)
        if self.children and not os.path.exists(source_path):
            source_path = self.md_filename(os.path.join(self.path, 'index'))
        return source_path

    @property
    def last_descendant(self):
        """
        Return the last descendant of the current node  (recursive).
        If the current node has no children, it's its own last descendant
        """
        if self.children:
            return self.children[-1].last_descendant
        else:
            return self

    @property
    def predecessor(self):
        """
        Return the object that precedes this one when reading end-to-end:
        - the last descendant of previous sibling (which might be the previous sibling itself)
        - the parent, or None.
        """
        idx = self.parent.children.index(self)
        if idx:  # there is a previous sibling
            return self.parent.children[idx - 1].last_descendant
        elif not self.parent.is_root():
            return self.parent
        else:
            return None

    @property
    def next_sibling_or_ancestor_sibling(self):
        """If the node has next sibling:
        """
        idx = self.parent.children.index(self)
        if idx + 1 < len(self.parent.children):
            # there is a next sibling
            return self.parent.children[idx + 1]
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
        if self.children:
            return self.children[0]
        else:
            return self.next_sibling_or_ancestor_sibling

    def md_filename(self, fn):
        return FILENAME_PATTERN % fn

    def to_dict(self):
        d = {
            'id': self.id,
            'class': self.__class__
        }
        if self.children:
            d['children'] = [c.to_dict() for c in self.children]
        if self.tags:
            d['tags'] = self.tags
        if self.config:
            d['config'] = repr(self.config)
        if self.title:
            d['title'] = self.title
        if self.summary:
            d['summary'] = self.summary

        return d

    @classmethod
    def from_config(cls, data, parent, root):
        if data.__class__ == dict:
            item = cls(data['id'], parent, root)
        else:
            item = cls(data, parent, root)

        if 'tags' in data:
            item.tags = data['tags']
        if 'config' in data:
            item.config = data['config']
        if item.__class__ == Part and cls.CHAPTERS in data:
            item.children = [Chapter.from_config(d, item, parent) for d in data[cls.CHAPTERS]]
        elif item.__class__ == Chapter and cls.SECTIONS in data:
            item.children = [Section.from_config(d, item, parent) for d in data[cls.SECTIONS]]

        return item

    def read_info(self):
        """Read info from content file."""
        self._read_info()

        for child in self.children:
            child.read_info()

    def _read_info(self):
        """Extract titles and summaries (and maybe later tags and other metadata) from a node."""
        if not os.path.exists(self.source_path):
            raise Exception("ERROR: source_path %s doesn't exist)" % self.path)
        with codecs.open(self.source_path, 'r', 'utf-8') as source:
            processor = mdp.MarkdownProcessor(source, filters=[
                partial(macros.MacroFilter.filter, ignore_unknown=True),
                mdp.MetadataPlugin.filter
            ])
            processor.process()
            logger.debug("node title: '%s'" % mdp.MetadataPlugin.title)
            self.title = mdp.MetadataPlugin.title
            self.summary = mdp.MetadataPlugin.summary

    def find(self, slug):
        """Find slug in this subtree"""
        if self.slug == slug:
            return self
        for child in self.children:
            res = child.find(slug)
            if res:
                return res
        else:
            return None


class ContentRoot(ContentNode):
    """
    A representation of entire content.

    The content has parts, the parts have chapters, and the chapters have sections.
    """
    def __init__(self, root_path):
        self.root_path = root_path
        super(ContentRoot, self).__init__(None, None, self)

    @classmethod
    def from_config(cls, structure, path=None):
        c = cls(path)
        c.root_path = path
        c.config = structure['config']
        c.children = [Part.from_config(part, c, c) for part in structure[cls.PARTS]]
        return c

    def to_dict(self):
        return {
            'config': self.config,
            'children': [p.to_dict() for p in self.children],
        }

    def read_info(self, content_path):
        """Read titles and structure etc. from content files."""
        self.root_path = content_path
        for part in self.children:
            part.read_info()

    @property
    def level(self):
        return 0

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
        if self.children:
            return self.children[0]
        else:
            return self.next_sibling_or_ancestor_sibling


class Part(ContentNode):
    @property
    def level(self):
        return 1


class Chapter(ContentNode):
    @property
    def level(self):
        return 2


class Section(ContentNode):
    @property
    def level(self):
        return 3
