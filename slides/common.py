# -*- coding: utf-8 -*-

import codecs
import markdown
import os
from operator import itemgetter
import yaml


SLIDE_MARKERS = ['---', '***', '* * *']
FILENAME_PATTERN = '%s.md'

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


def make_pathname(name):
    return name.lower().replace(" ", '-')


def md_filename(name):
    return FILENAME_PATTERN % make_pathname(name)


def make_title(name):
    return name.title().replace('s3', 'S3')


def create_directory(directory):
    if not os.path.exists(directory):
        os.mkdir(directory)


def get_config(filename):
    return parse_config(read_config(filename))


def read_config(filename):
    stream = open(filename, "r")
    return yaml.load(stream)


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
            c.introduction = Part.from_config(data[CONTENT][FRONT_MATTER], FRONT_MATTER)
            c.chapters = [Chapter.from_config(chapter, id=idx) for idx, chapter in enumerate(data[CONTENT][CHAPTERS], 1)]
            c.appendix = Part.from_config(data[CONTENT][APPENDIX], APPENDIX)

            c.title = data[CONTENT].get(TITLE)
            c.end = data[CONTENT].get(END)

        else:
            # parse old config format
            c.introduction = Part.from_config(data[FRONT_MATTER], FRONT_MATTER)
            c.chapters = [Chapter.from_config(data[CHAPTERS][chapter_name], id=idx, name=chapter_name) for idx, chapter_name in enumerate(data[CHAPTER_ORDER], 1)]
            c.appendix = Part.from_config(data[APPENDIX], APPENDIX)

            c.title = data.get(TITLE)
            c.end = data.get(END)
        return c

    def to_dict(self):
        return {
            TITLE: self.title,
            FRONT_MATTER: self.introduction.to_dict(),
            CHAPTERS: [c.to_dict() for c in self.chapters],
            APPENDIX: self.appendix.to_dict(),
            END: self.end,
            INDEX: self.index,
        }


class ContentItem(object):

    def __init__(self, title=None, slug=None):
        self.title = title
        self.slug = slug

    def md_filename(self, name):
        return FILENAME_PATTERN % self.slug

    def to_dict(self):
        return {
            TITLE: self.title,
            SLUG: self.slug,
        }


class Part(ContentItem):
    """INtroduction or Appendix."""
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
            title = make_title(name)
            slug = make_pathname(name)
        if type(data) == dict:
            if TITLE in data:
                title = data[TITLE]
            if SLUG in data:
                slug = data[SLUG]
            section_source = data[SECTIONS]
        elif type(data) == list:
            section_source = data
        return cls(title, slug), section_source

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


def parse_config_new(data):
    """
    Parse raw config data structure into efficient in-memory structure.

    Parse raw config data structure into efficient in-memory structure.

    returns a dictionary with the config as a dictionary, that contains a Content object at index 'content'
    """

    def parse_chapter(item, idx):
        new_item = {ID: idx}
        if SECTIONS in item:
            new_item[TITLE] = item[TITLE]
            new_item[SLUG] = item[SLUG]
            if SLUG not in item:
                new_item[SLUG] = make_pathname(item[TITLE])
            elif TITLE not in item:
                new_item[TITLE] = make_title(item[SLUG])
            sections = item[SECTIONS]
        else:
            name = item.keys()[0]
            new_item[TITLE] = make_title(name)
            new_item[SLUG] = make_pathname(name)
            sections = item[name]
        new_item[SECTIONS] = [Section.from_config_item(s, idx, sidx) for sidx, s in enumerate(sections, 1)]
        return new_item


    data['CONTENT'] = Content.from_config(data)
    # TODO: delete legacy structures for intro, appendix, chapter order etc. 
    # data[INDEX] = []
    # for chapter in data[CONTENT][CHAPTERS]:
    #     for section in chapter[SECTIONS]:
    #         data[INDEX].append(section)
    # data[INDEX].sort(key=itemgetter(TITLE))
    return data


def parse_config(data):
    """
    Parse raw config data structure into efficient in-memory structure.

    content: each node contains slug and title.
    """
    def parse_element(item, name, idx=None):
        """Parse introduction, appendix and old-style chapters."""
        new_item = {}
        # set defaults:
        new_item[TITLE] = make_title(name)
        new_item[SLUG] = make_pathname(name)
        if idx:
            new_item[ID] = idx
        if type(item) == dict:
            if TITLE in item:
                new_item[TITLE] = item[TITLE]
            if SLUG in item:
                new_item[SLUG] = item[SLUG]
            sections = item[SECTIONS]
        elif type(item) == list:
            sections = item
        new_item[SECTIONS] = [parse_section(s, idx, sidx) for sidx, s in enumerate(sections, 1)]
        return new_item

    def parse_chapter(item, idx):
        new_item = {ID: idx}
        if SECTIONS in item:
            new_item[TITLE] = item[TITLE]
            new_item[SLUG] = item[SLUG]
            if SLUG not in item:
                new_item[SLUG] = make_pathname(item[TITLE])
            elif TITLE not in item:
                new_item[TITLE] = make_title(item[SLUG])
            sections = item[SECTIONS]
        else:
            name = item.keys()[0]
            new_item[TITLE] = make_title(name)
            new_item[SLUG] = make_pathname(name)
            sections = item[name]
        new_item[SECTIONS] = [parse_section(s, idx, sidx) for sidx, s in enumerate(sections, 1)]
        return new_item

    def parse_section(item, cidx=None, sidx=None):
        if type(item) == str:
            section = {}
            section[SLUG] = make_pathname(item)
            section[TITLE] = make_title(item)
        else:
            section = item
        if cidx:
            section[CHAPTER_ID] = cidx
        if sidx:
            section[ID] = sidx
        return section

    content = {}
    if CONTENT in data:
        # parse new config format
        content[FRONT_MATTER] = parse_element(data[CONTENT][FRONT_MATTER], FRONT_MATTER)
        content[CHAPTERS] = []
        content[CHAPTERS] = [parse_chapter(chapter, idx) for idx, chapter in enumerate(data[CONTENT][CHAPTERS], 1)]
        content[APPENDIX] = parse_element(data[CONTENT][APPENDIX], APPENDIX)

        content[TITLE] = data[CONTENT].get(TITLE, TITLE)
        content[END] = data[CONTENT].get(END, END)

        data[CONTENT] = content
    else:
        # parse old config format
        content[FRONT_MATTER] = parse_element(data[FRONT_MATTER], FRONT_MATTER)
        del(data[FRONT_MATTER])
        content[CHAPTERS] = [parse_element(data[CHAPTERS][chapter_name], chapter_name, idx) for idx, chapter_name in enumerate(data[CHAPTER_ORDER], 1)]
        del data[CHAPTERS]
        del data[CHAPTER_ORDER]
        content[APPENDIX] = parse_element(data[APPENDIX], APPENDIX)
        del(data[APPENDIX])

        content[TITLE] = data.get(TITLE, TITLE)
        if TITLE in data:
            del data[TITLE]
        content[END] = data.get(END, END)
        if END in data:
            del data[END]

        data[CONTENT] = content

    data[INDEX] = []
    for chapter in data[CONTENT][CHAPTERS]:
        for section in chapter[SECTIONS]:
            data[INDEX].append(section)
    data[INDEX].sort(key=itemgetter(TITLE))
    return data


def increase_headline_level(line):
    line = '#' + line
    if line.endswith('#'):
        line = line + '#'
    return line


def markdown2html(text):
    return markdown.markdown(text, ['markdown.extensions.extra', 'markdown.extensions.meta'])


def make_headline_prefix(commandline_args, config, chapter_idx, section_idx):
    if commandline_args.section_prefix:
        template = codecs.decode(commandline_args.section_prefix, 'utf-8')
    else:
        template = config.get('section-prefix', None)
    if template:
        return template % dict(chapter=chapter_idx, section=section_idx)
    else:
        return None


class LineWriter(object):

    def __init__(self, target, newlines):
        self.target = target
        if not newlines:
            self.newlines = '\n'
        else:
            self.newlines = newlines
        self.prev_line_empty = False

    def write(self, line):
        """Write line to target, reset blank line counter, output newline if necessary."""
        if self.prev_line_empty:
            self.target.write(self.newlines)
        self.target.write(line.rstrip())
        self.target.write(self.newlines)
        self.prev_line_empty = False

    def mark_empty_line(self):
        self.prev_line_empty = True
