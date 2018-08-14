#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Build a slide deck (either in Deckset format or as reveal.js.
"""

from __future__ import unicode_literals

import codecs
import os
import re
import sys
from shutil import copyfile

from common import make_pathname, make_title, create_directory, read_config, get_config
from common import TITLE, FRONT_MATTER, CHAPTERS, APPENDIX, END, SKIP

from glossary import read_glossary
import translate

from build_deckset_slides import DecksetWriter
from build_revealjs_slides import RevealJsWriter, RevealJSBuilder
from build_web_content import cmd_convert_to_web
from build_jekyll import JekyllWriter
from ebook_builder import EbookWriter
from revealjs_converter import RevealJsHtmlConverter

TMP_FOLDER = 'tmp-groups'


translate.read_translation_memory('content/localization.po')


def cmd_build_slides(args):
    """Build slides decks"""

    if args.format == 'revealjs':
        build_reveal_slides(args)
    elif args.format == 'deckset':
        build_deckset_slides(args)
    elif args.format == 'wordpress':
        build_wordpress(args)
    elif args.format == 'jekyll':
        j = JekyllWriter(args)
        j.build()
    elif args.format == 'ebook':
        e = EbookWriter(args)
        e.build()
    else:
        print("unknown format", args.format)
        sys.exit(1)


def cmd_convert_slides(args):
    """Convert a file in deckset format to a reveal.js presentation (html)."""

    cw = RevealJsHtmlConverter(args.source)
    rw = RevealJsWriter(args.target, args.template, cw)
    rw.build()


def cmd_compile_slides(args):
    """Compile slides from sources into one file per chapter."""
    c = SectionCompiler(args)
    c.compile_content()


def build_deckset_slides(args):
    """Create a source file for a deckset presentation."""
    r = DecksetWriter(args)
    r.build()


def build_reveal_slides(args):
    """
    Build reveal.js presentation. <target> is a file inside the reveal.js folder,
    template.html is expected in the same folder.
    """
    cw = RevealJSBuilder(args.config, args.source, args.glossary, args.glossary_items)
    rw = RevealJsWriter(args.target, args.template, cw)
    rw.build()


def build_wordpress(args):
    cmd_convert_to_web(args)


def cmd_create_source_files_for_slides(args):
    """Create dummy source files for slides. If file or folder exists, don't touch it."""

    create_directory(args.target)
    config = read_config(args.config)

    def make_group(group_name, source):
        # create group dir
        group_root = os.path.join(args.target, make_pathname(group_name))
        create_directory(group_root)
        # create group index file
        make_file(group_root, "index", group_name, '#')
        # create individual sections (add section name as headline)
        for section in source:
            make_file(group_root, section, section, '##')

    def make_file(root, filename_root, title_root, markup='#'):
        """Create file if it does not exist."""
        filename = os.path.join(root, '%s.md' % make_pathname(filename_root))
        if not os.path.exists(filename):
            with codecs.open(filename, 'w+', 'utf-8') as fp:
                fp.write('%s %s\n\n' % (markup, make_title(title_root)))
        else:
            if args.verbose:
                print "skipped %s" % title_root

    make_file(args.target, 'title', 'title')
    if FRONT_MATTER in config:
        make_group(FRONT_MATTER, config[FRONT_MATTER])
    for chapter in config[CHAPTERS].keys():
        make_group(chapter, config[CHAPTERS][chapter])
    if APPENDIX in config:
        make_group(APPENDIX, config[APPENDIX])
    end = config.get(END, END)
    if end != SKIP:
        make_file(args.target, 'end', 'end')


class SectionCompiler():
    """Compile all source files relevant for building the slide deck:
        - title
        - front-matter
        - all chapters
        - appendix
        - end
        into the temp folder.

    Chapters can optionally be prefixed with a title slide, an image slide, or both."""

    GROUP_INDEX_FILENAME = 'index.md'
    CHAPTER_INDEX_IMAGE = '\n![inline,fit](img/grouped-patterns/group-%s.png)\n\n'
    CHAPTER_TITLE_IMAGE = '\n![inline,fit](img/pattern-group-headers/header-group-%s.png)\n\n'
    DEFINE_PATTERN = re.compile("\{\{define\:(?P<name>.*)\}\}")
    GLOSSARY_PATTERN = re.compile("\{\{glossary\:(?P<name>.*)\}\}")

    def __init__(self, args):
        self.args = args
        self.source = self.args.source
        self.target_folder = args.target

        self.INSERT_CHAPTER_TEXT_TITLE_SLIDE = False
        self.INSERT_CHAPTER_IMG_TITLE_SLIDE = False
        if self.args.chapter_title == 'img':
            self.INSERT_CHAPTER_IMG_TITLE_SLIDE = True
        elif self.args.chapter_title == 'text':
            self.INSERT_CHAPTER_TEXT_TITLE_SLIDE = True
        elif self.args.chapter_title == 'both':
            self.INSERT_CHAPTER_IMG_TITLE_SLIDE = True
            self.INSERT_CHAPTER_TEXT_TITLE_SLIDE = True
        self.config = get_config(self.args.config)

        self.glossary = read_glossary(self.args.glossary)

    def compile_content(self):
        """Compile all source files relevant for building the slide deck:
            - title
            - introduction
            - all chapters
            - appendix
            - end
            into the temp folder."""

        if not os.path.exists(self.target_folder):
            os.makedirs(self.target_folder)
        content = self.config['content']
        if TITLE in content and content[TITLE] != SKIP:
            self._copy_file('%s.md' % content[TITLE])
        if FRONT_MATTER in content:
            self._compile_section_group(content[FRONT_MATTER])

            # insert illustrations for all chapters between intro and chapters
            if self.args.add_chapter_illustration:
                for chapter in content['chapters']:
                    self.target.write(self.GROUP_INDEX_IMAGE % str(chapter['index']))
                    self._append_section_break()
        for chapter in content['chapters']:
                self._compile_section_group(chapter)
        if APPENDIX in content:
            self._compile_section_group(content[APPENDIX])
        if END in content and content[END] != SKIP:
            self._copy_file('%s.md' % content[END])

    def _copy_file(self, name):
        copyfile(os.path.join(self.source, name), os.path.join(self.target_folder, name))

    def _compile_section_group(self, group):
        """Compile front matter, chapters and appendix."""
        folder = os.path.join(self.source, group['slug'])

        def is_chapter():
            return 'index' in group

        with codecs.open(os.path.join(self.target_folder, '%s.md' % group['slug']), 'w+', 'utf-8') as self.target:
            if is_chapter():
                # chapter title and index slides
                if self.INSERT_CHAPTER_TEXT_TITLE_SLIDE:
                    self.target.write('\n# %s. %s' % (group['index'], group['title']))
                    self._slide_break()
                if self.INSERT_CHAPTER_IMG_TITLE_SLIDE:
                    self.target.write(self.CHAPTER_TITLE_IMAGE % str(group['index']))
                    self._slide_break()
                if self.args.add_chapter_illustration:
                    self.target.write(self.CHAPTER_INDEX_IMAGE % str(group['index']))
                    self._slide_break()

            # insert group preamble if present
            if os.path.exists(os.path.join(folder, self.GROUP_INDEX_FILENAME)):
                self._append_section(folder, self.GROUP_INDEX_FILENAME)
                self._slide_break()

            # add individual sections
            for section in group['sections']:
                if is_chapter() and self.args.section_prefix:
                    headline_prefix = self.args.section_prefix % dict(chapter=group['index'], section=section['index'])
                else:
                    headline_prefix = None
                self._append_section(folder, '%s.md' % section['slug'], headline_prefix)
                if section['index'] < len(group['sections']):
                    self._slide_break()

    def _slide_break(self):
        self.target.write('\n\n---\n\n')

    def _append_section(self, folder, name, headline_prefix=None):
        """
        Append a section to self.target, if headline prefix is given,
        add that to the first headline of the section.
        """

        def glossary_replace(match, key, pattern):
            """Get a definition of a term from the glossary."""
            name = match.group('name')
            return pattern % self.glossary['terms'][name][key]

        def insert_definition(match):
            return glossary_replace(match, 'definition', "_%s_")

        def insert_glossary_term(match):
            return glossary_replace(match, 'glossary', "%s")

        with codecs.open(os.path.join(folder, name), 'r', 'utf-8') as section:
            if headline_prefix:
                # insert pattern number into first headline of file
                line = section.next()
                try:
                    pos = line.index('# ')
                except ValueError():
                    raise Exception(
                        "no headline in first line of %s" % os.path.join(folder, name))
                self.target.write(
                    ' '.join((line[:pos + 1], codecs.decode(headline_prefix, 'utf-8'), line[pos + 1:].lstrip())))
            for line in section:
                if self.glossary:
                    # replace definitions from glossary
                    line = self.DEFINE_PATTERN.sub(insert_definition, line)
                    line = self.GLOSSARY_PATTERN.sub(insert_glossary_term, line)
                self.target.write(line)
