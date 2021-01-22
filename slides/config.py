# -*- coding: utf-8 -*-

from __future__ import print_function

import os
from operator import attrgetter
import codecs

import sys
from functools import partial
from pprint import pformat
import markdown_processor as mdp
from common import read_config_file, FILENAME_PATTERN

# section names
PARTS = 'parts'
CHAPTERS = 'chapters'
SECTIONS = 'sections'
# attribute for title
TITLE = 'title'


def get_config(filename):
    raise Exception("this no longer works as intended!!")


def get_project_config(filename, preset):
    """Get a config object for the selected preset."""
    # TODO: when all is refactored, rename that to config again??
    config_data = read_config_file(filename)
    cfg = ConfigObject(config_data['defaults'], config_data['presets'][preset])
    print("------- config ---------")
    print(cfg)
    return cfg


def get_structure(filename, content_path):
    print("------- structure---------")
    print(read_config_file(filename))

    cs = ContentStructure.from_config(read_config_file(filename))
    cs.read_info(content_path)
    #print(pformat(cs.to_dict()))
    return cs


def make_title(name):
    return name.title().replace('s3', 'S3')


class ConfigObject(object):

    def __init__(self, default_config_data, preset_data=None):
        if default_config_data:
            self._build_structure(default_config_data)
        if preset_data:
            self._update(preset_data)

    def _build_structure(self, data):
        for key, value in data.items():
            if value.__class__ == dict:
                self.__dict__[key] = ConfigObject(value)
            elif value.__class__ == list:
                self.__dict__[key] = self.build_list(value)
            else:
                self.__dict__[key] = value

    @classmethod
    def build_list(cls, list_data):
        """Build nested list that contains content objects for all dictionaries"""
        result = []
        for item in list_data:
            if item.__class__ == list:
                result.append(ConfigObject.build_list(item))
            elif item.__class__ == dict:
                result.append(ConfigObject(item))
            else:
                result.append(item)
        return result

    def _update(self, data):
        """Update from data structure"""
        for key, value in data.items():
            print(key, value)
            if value.__class__ == dict:
                raise Exception("can't update dictionary (yet)")
                # self.__dict__[key] = ConfigObject(value)
            elif value.__class__ == list:
                if hasattr(self, key):
                    raise Exception("can't update list (yet)", key)
                else:
                    self.__dict__[key] = self.build_list(value)
            else:
                self.__dict__[key] = value

    def __repr__(self):
        return repr(self.__dict__)

class ContentStructure(object):
    """
    A representation of entire content.

    The content has parts, the parts have chapters, and the chapters have sections.
    """
    def __init__(self):
        self.parts = []
        self.path = ''
        self.config = {}
        self.id = ''

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
        source_path = self.md_filename(self.path)
        if self.children and not os.path.exists(source_path):
            source_path = self.md_filename(os.path.join(self.path, 'index'))
        with codecs.open(source_path, 'r', 'utf-8') as source:
            processor = mdp.MarkdownProcessor(source, filters=[
                # TODO: get glossary
                #partial(mdp.inject_glossary, self.glossary),
                mdp.MetadataPlugin.filter
            ])
            processor.process()
            #print(mdp.MetadataPlugin.title)
            #print(mdp.MetadataPlugin.summary)
            self.title = mdp.MetadataPlugin.title
            self.summary = mdp.MetadataPlugin.summary



class Part(ContentNode):
    pass


class Chapter(ContentNode):
    pass


class Section(ContentNode):
    pass
