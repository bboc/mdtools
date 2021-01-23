# -*- coding: utf-8 -*-
from __future__ import print_function

import os
import codecs

import markdown_processor as mdp
from common import read_config_file, FILENAME_PATTERN

# section names
PARTS = 'parts'
CHAPTERS = 'chapters'
SECTIONS = 'sections'
# attribute for title
TITLE = 'title'


def get_structure(filename, content_path):
    print("------- structure---------")
    print(filename)

    cs = ContentStructure.from_config(read_config_file(filename))
    cs.read_info(content_path)
    # print(pformat(cs.to_dict()))
    return cs


class ContentStructure(object):
    """
    A representation of entire content.

    The content has parts, the parts have chapters, and the chapters have sections.
    """
    def __init__(self):
        self.children = []
        self.path = ''
        self.config = {}
        self.id = ''
        self.relpath = ''

    @classmethod
    def from_config(cls, structure, path=None):
        c = cls()
        c.path = path
        c.config = structure['config']
        c.parts = [Part.from_config(part, c, c) for part in structure[PARTS]]
        # TODO: raise exception for wrong config format and sys.exit(1)
        return c

    def to_dict(self):
        return {
            'config': self.config,
            'parts': [p.to_dict() for p in self.parts],
        }

    def read_info(self, content_path):
        """Read titles and structure etc. from content files."""
        self.path = content_path
        for part in self.parts:
            part.read_info()


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
    def __init__(self, slug, parent, root):
        pass
        self.parent = parent
        self.root = root
        self.slug = slug
        self.children = []
        self.title = 'to title set'
        self.config = {}
        self.tags = []
        self.summary = None

    @property
    def id(self):
        return '.'.join((self.parent.id, self.slug))

    @property
    def path(self):
        return os.path.join(self.parent.path, self.slug)

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
            return self.children[-1].last_descendant()
        else:
            return self

    @property
    def next_sibling_of_the_closest_ancestor(self):
        return None

    @property
    def predecessor(self):
        """
        Return the object that precedes this one when reading end-to-end:
        - the last descendant of previous sibling (which might be the previous sibling itself)
        - the parent, or None.
        """
        idx = self.parent.children.index(self)
        if idx:  # there is a previois sibling
            return self.parent.children[idx - 1].last_descendant()
        if self.parent.__class__ is ContentNode:
            return self.parent
        else:
            return None

    @property
    def successor(self):
        """
        Return the object that succedes this one when reading end-to-end:
        - the first child
        - the next sibling,
        - the next sibling of the closest ancestor that has one (recursive)
        - None
        """
        if self.children:
            return self.children[0]
        idx = self.parent.children.index(self)
        if idx + 1 <= len(self.parent.children):
            return self.parent.children[idx + 1]
        # might be None
        return self.next_sibling_of_the_closest_ancestor()

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
        if item.__class__ == Part and CHAPTERS in data:
            item.children = [Chapter.from_config(d, item, parent) for d in data[CHAPTERS]]
        elif item.__class__ == Chapter and SECTIONS in data:
            item.children = [Section.from_config(d, item, parent) for d in data[SECTIONS]]

        return item

    def read_info(self):
        """Read info from content file."""
        self._read_info()

        for child in self.children:
            child.read_info()

    def _read_info(self):
        """Extract titles and summaries (and maybe later tags and other metadata) from a node."""

        with codecs.open(self.source_path, 'r', 'utf-8') as source:
            processor = mdp.MarkdownProcessor(source, filters=[
                # TODO: get glossary
                # partial(mdp.inject_glossary, self.glossary),
                mdp.MetadataPlugin.filter
            ])
            processor.process()
            # print(mdp.MetadataPlugin.title)
            # print(mdp.MetadataPlugin.summary)
            self.title = mdp.MetadataPlugin.title
            self.summary = mdp.MetadataPlugin.summary


class Part(ContentNode):
    pass


class Chapter(ContentNode):
    pass


class Section(ContentNode):
    pass
