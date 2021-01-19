# -*- coding: utf-8 -*-

from __future__ import print_function

from operator import attrgetter
import sys
import yaml


from common import make_pathname, FILENAME_PATTERN

# section names
PARTS = 'parts'
CHAPTERS = 'chapters'
SECTIONS = 'sections'


"""

TODO:

set root path
extract titles and summaries from files

make_path …

"""

def get_config(filename):
    return parse_config(read_config(filename))


def read_config(filename):
    stream = open(filename, "r")
    return yaml.load(stream)


def parse_config(data):
    """
    Parse raw config data structure into efficient in-memory structure.

    Return a dictionary with the config as a dictionary, that contains a Content object at index 'content'
    """
    # data[CONTENT] = Content.from_config(data)
    print(repr(data))
    print(repr(Content.from_config(data)))
    # return data


def make_title(name):
    return name.title().replace('s3', 'S3')


class ConfigObject(object):

    def __init__(self, basic_config, output_format=None):
        if basic_config:
            self._build_structure(basic_config)
        if output_format:
            self._update(output_format)

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
        print(repr(data))
        for key, value in data.items():
            if value.__class__ == dict:
                pass # self.__dict__[key] = ConfigObject(value)
            elif value.__class__ == list:
                pass
            else:
                self.__dict__[key] = value


class Content(object):
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
    def from_config(cls, structure, path):
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
        self.title = None
        self.config = {}
        self.tags = []

    @property
    def id(self):
        return '.'.join((self.parent.id, self.slug))

    def md_filename(self):
        return FILENAME_PATTERN % self.slug

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
        return d

    @classmethod
    def from_config(cls, data, parent, root):
        item = cls(data['id'], parent, root)
        if 'tags' in data:
            item.tags = data['tags']
        if 'config' in data:
            item.config = data['config']
        if item.__class__ == Part and CHAPTERS in data:
            item.children = [Chapter.from_config(d, item, parent) for d in data[CHAPTERS]]

        elif item.__class__ == Chapter and SECTIONS in data:
            item.children = [Section.from_config(d, item, parent) for d in data[SECTIONS]]

        return item


class Part(ContentNode):
    pass


class Chapter(ContentNode):
    pass


class Section(ContentNode):
    pass
