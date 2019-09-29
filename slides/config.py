# -*- coding: utf-8 -*-

from __future__ import print_function

from operator import attrgetter
import sys
import yaml


from common import make_pathname, FILENAME_PATTERN

# section names
CHAPTER_ORDER = 'chapter-order'
TITLE = 'title'
FRONT_MATTER = 'introduction'
CHAPTERS = 'chapters'
APPENDIX = 'appendix'
END = 'end'
SKIP = 'SKIP'
SLUG = 'slug'
CONTENT = 'content'
SECTIONS = 'sections'
CHAPTER_ID = 'chapter_id'
ID = 'id'
INDEX = 'index'


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
    data[CONTENT] = Content.from_config(data)
    return data


def make_title(name):
    return name.title().replace('s3', 'S3')


class Content(object):
    def __init__(self):
        self.title = None
        self.introduction = None
        self.chapters = []
        self.appendix = None
        self.end = None
        self.index = None

    @classmethod
    def from_config(cls, data):
        c = cls()
        if CONTENT in data:
            # parse new config format
            if FRONT_MATTER in data[CONTENT]:
                c.introduction = Part.from_config(data[CONTENT][FRONT_MATTER], FRONT_MATTER)
            c.chapters = [Chapter.from_config(chapter, id=idx) for idx, chapter in enumerate(data[CONTENT][CHAPTERS], 1)]
            if APPENDIX in data[CONTENT]:
                c.appendix = Part.from_config(data[CONTENT][APPENDIX], APPENDIX)

            c.title = data[CONTENT].get(TITLE)
            c.end = data[CONTENT].get(END)

        elif CHAPTER_ORDER in data:
            # parse old config format
            if FRONT_MATTER in data:
                c.introduction = Part.from_config(data[FRONT_MATTER], FRONT_MATTER)
            if CHAPTERS in data:
                c.chapters = [Chapter.from_config(data[CHAPTERS][chapter_name], id=idx, name=chapter_name) for idx, chapter_name in enumerate(data[CHAPTER_ORDER], 1)]
            else:
                # parse slide deck format (chapters are inferred from key chapter_order)
                c.chapters = [Chapter(title=make_title(chapter_name), slug=make_pathname(chapter_name), id=idx) for idx, chapter_name in enumerate(data[CHAPTER_ORDER], 1)]

            if APPENDIX in data:
                c.appendix = Part.from_config(data[APPENDIX], APPENDIX)

            c.title = data.get(TITLE)
            c.end = data.get(END)

            # remove info containing structure infromation from config data

            for key in [TITLE, FRONT_MATTER, CHAPTER_ORDER, CHAPTERS, APPENDIX, END]:
                if key in data:
                    del data[key]
        else:
            print("unknown config file format")
            sys.exit(1)

        # remove skip markers
        if c.title == SKIP:
            c.title = None
        if c.end == SKIP:
            c.end = None
        c.index = []

        for chapter in c.chapters:
            for section in chapter.sections:
                c.index.append(section)
            c.index.sort(key=attrgetter(TITLE))
        return c

    def to_dict(self):
        if self.introduction:
            introduction = self.introduction.to_dict()
        else:
            introduction = None
        if self.appendix:
            appendix = self.appendix.to_dict()
        else:
            appendix = None
        return {
            TITLE: self.title,
            FRONT_MATTER: introduction,
            CHAPTERS: [c.to_dict() for c in self.chapters],
            APPENDIX: appendix,
            END: self.end,
            INDEX: [i.to_dict() for i in self.index],
        }


class ContentItem(object):

    def __init__(self, title=None, slug=None):
        self.title = title
        self.slug = slug

    def md_filename(self):
        return FILENAME_PATTERN % self.slug

    def to_dict(self):
        return {
            TITLE: self.title,
            SLUG: self.slug,
        }


class Part(ContentItem):
    """Introduction or Appendix."""
    def __init__(self, title, slug, sections=None):
        super(Part, self).__init__(title, slug)
        if sections:
            self.sections = sections
        else:
            self.sections = []

    @classmethod
    def from_config(cls, data, name):
        """
        item is either {
            [slug: … ]
            [title: …]
            sections […]
        }
        or [section1, section2, …]
        """
        part, section_source = cls._make_basic_item_from_config(data, name)
        part.sections = [Section.from_config(s, sidx) for sidx, s in enumerate(section_source, 1)]
        return part

    @classmethod
    def _make_basic_item_from_config(cls, data, name=None):
        if name:
            # set defaults
            title = make_title(name)
            slug = make_pathname(name)
        if type(data) == dict:
            # extended style (2 variants)
            if SECTIONS in data:
                """{
                [slug: … ]
                [title: …]
                sections […]
                }"""
                if TITLE in data:
                    title = data[TITLE]
                if SLUG in data:
                    slug = data[SLUG]
                section_source = data[SECTIONS]
            else:
                """{chapter-name: [section1, section2, …]}"""
                name = data.keys()[0]
                title = make_title(name)
                slug = make_pathname(name)
                section_source = data[name]
        elif type(data) == list:
            # simple style (data contains sections, slug and title derived from name)
            section_source = data
        return cls(title, slug), section_source

    def is_chapter(self):
        return False

    def to_dict(self):
        d = super(Part, self).to_dict()
        d.update({
            SECTIONS: [s.to_dict() for s in self.sections],
        })
        return d


class Chapter(Part):
    def __init__(self, title=None, slug=None, id=None):
        super(Chapter, self).__init__(title, slug, [])
        self.id = id

    @classmethod
    def from_config(cls, data, name=None, id=None):
        chapter, section_source = super(Chapter, cls)._make_basic_item_from_config(data, name)
        chapter.id = id
        chapter.sections = [Section.from_config(s, sidx, chapter.id) for sidx, s in enumerate(section_source, 1)]
        return chapter

    def is_chapter(self):
        return True

    def to_dict(self):
        d = super(Chapter, self).to_dict()
        d.update({
            ID: self.id,
        })
        return d


class Section(ContentItem):

    def __init__(self, title=None, slug=None, id=None, chapter_id=None):
        super(Section, self).__init__(title, slug)
        self.id = id
        self.chapter_id = chapter_id

    @classmethod
    def from_config(cls, item, id=None, chapter_id=None):
        if type(item) == str:
            title = make_title(item)
            slug = make_pathname(item)
        else:
            title = item[TITLE]
            slug = item[SLUG]
        return cls(title, slug, id, chapter_id)

    def to_dict(self):
        d = super(Section, self).to_dict()
        d[ID] = self.id
        if self.chapter_id is not None:
            d[CHAPTER_ID] = self.chapter_id
        return d

