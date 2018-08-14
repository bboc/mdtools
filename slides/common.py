#!/usr/bin/env python

import codecs
import os
import yaml
import markdown


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


def make_pathname(name):
    return name.lower().replace(" ", '-')


def md_filename(name):
    return FILENAME_PATTERN % make_pathname(name)


def make_title(name):
    return name.title().replace('s3', 'S3')


def create_directory(directory):
    if not os.path.exists(directory):
        os.mkdir(directory)


def read_config(filename):
    stream = open(filename, "r")
    return yaml.load(stream)


def parse_config(data):
    """
    Parse raw config data structure into efficient in-memory structure.

    content: each node contains slug and title.
    """
    def parse_element(item, name):
        new_item = {}
        # set defaults:
        new_item['sections'] = []
        new_item['title'] = make_title(name)
        new_item['slug'] = make_pathname(name)
        if type(item) == dict:
            if 'title' in item:
                new_item['title'] = item['title']
            if 'slug' in item:
                new_item['slug'] = item['slug']
            for s in item['sections']:
                new_item['sections'].append(parse_section(s))
        elif type(item) == list:
            for s in item:
                new_item['sections'].append(parse_section(s))
        return new_item

    def parse_chapter(item):
        new_item = {}
        new_item['sections'] = []
        if 'sections' in item:
            new_item['title'] = item['title']
            new_item['slug'] = item['slug']
            if 'slug' not in item:
                new_item['slug'] = make_pathname(item['title'])
            elif 'title' not in item:
                new_item['title'] = make_title(item['slug'])
            for s in item['sections']:
                new_item['sections'].append(parse_section(s))
        else:
            name = item.keys()[0]
            new_item['title'] = make_title(name)
            new_item['slug'] = make_pathname(name)

            for s in item[name]:
                new_item['sections'].append(parse_section(s))
        return new_item

    def parse_section(item):
        if type(item) == str:
            new_item = {}
            new_item['slug'] = make_pathname(item)
            new_item['title'] = make_title(item)
            return new_item
        else:
            return item

    if 'content' in data:
        # parse new config format
        content = {}
        content['introduction'] = parse_element(data['content']['introduction'], 'introduction')
        content['chapters'] = []
        for chapter in data['content']['chapters']:
            content['chapters'].append(parse_chapter(chapter))
        content['appendix'] = parse_element(data['content']['appendix'], 'appendix')
        if TITLE in data['content']:
            content[TITLE] = data['content'][TITLE]
        else:
            content[TITLE] = SKIP
        if END in data['content']:
            content[END] = data['content'][END]
        else:
            content[END] = SKIP

        data['content'] = content
    else:
        # pass old config format
        pass
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
