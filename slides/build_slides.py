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

from common import make_pathname, make_title, create_directory, read_config
from glossary import read_glossary

from build_deckset_slides import DecksetWriter
from build_revealjs_slides import RevealJsWriter, RevealJSBuilder
from build_web_content import cmd_convert_to_web
from revealjs_converter import RevealJsHtmlConverter

TMP_FOLDER = 'tmp-groups'


def cmd_build_slides(args):
    """Build slides decks"""

    if args.format == 'revealjs':
        build_reveal_slides(args)
    elif args.format == 'deckset':
        build_deckset_slides(args)
    elif args.format == 'wordpress':
        build_wordpress(args)
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
    if 'introduction' in config:
        make_group('introduction', config['introduction'])
    for chapter in config['chapters'].keys():
        make_group(chapter, config['chapters'][chapter])
    if 'closing' in config:
        make_group('closing', config['closing'])
    make_file(args.target, 'end', 'end')


class SectionCompiler():
    """Compile all source files relevant for building the slide deck:
        - title
        - introduction
        - all chapters
        - closing
        - end
        into the temp folder.

    Chapters can optionally be prefixed with a title slide, an image slide, or both."""

    # TODO: add those as defaults, and read from config
    CHAPTER_NUMBER = ' Pattern %s.%s:'

    GROUP_INDEX_FILENAME = 'index.md'
    CHAPTER_INDEX_IMAGE = '\n![inline,fit](img/grouped-patterns/group-%s.png)\n\n'
    CHAPTER_TITLE_IMAGE = '\n![inline,fit](img/pattern-group-headers/header-group-%s.png)\n\n'
    DEFINE_PATTERN = re.compile("\{\{define\:(?P<name>.*)\}\}")

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
        self.config = read_config(self.args.config)

        self.glossary = read_glossary(self.args.glossary)

    def compile_content(self):
        """Compile one all source files relevant for building the slide deck:
            - title
            - introduction
            - all chapters
            - closing
            - end
            into the temp folder."""

        if not os.path.exists(self.target_folder):
            os.makedirs(self.target_folder)

        # title
        self._copy_file('title.md')
        # intro
        if 'introduction' in self.config:
            self._compile_section_group(self.config['introduction'], 'introduction')

            # insert illustrations for all chapters between intro and chapters
            if self.args.add_chapter_illustration:
                for i, chapter in enumerate(self.config['chapter_order']):
                    self.target.write(self.GROUP_INDEX_IMAGE % str(i + 1))
                    self._append_section_break()

        # chapters
        for i, chapter in enumerate(self.config['chapter_order']):
                self._compile_section_group(self.config['chapters'][chapter], chapter, i + 1)
        # closing
        if 'closing' in self.config:
            self._compile_section_group(self.config['closing'], 'closing')
        # end
        try:
            self._copy_file('end.md')
        except IOError:
            print "WARNING: missing end.md"

    def _copy_file(self, name):
        copyfile(os.path.join(self.source, name), os.path.join(self.target_folder, name))

    def _compile_section_group(self, group, group_name, chapter_index=None):
        """Compile intros, chapters and closing."""
        folder = os.path.join(self.source, make_pathname(group_name))

        def is_chapter():
            return chapter_index

        with codecs.open(os.path.join(self.target_folder, '%s.md' % make_pathname(group_name)), 'w+', 'utf-8') as self.target:
            if is_chapter():
                # chapter title and index slides
                if self.INSERT_CHAPTER_TEXT_TITLE_SLIDE:
                    self.target.write('\n# %s. %s' % (chapter_index, make_title(group_name)))
                    self._slide_break()
                if self.INSERT_CHAPTER_IMG_TITLE_SLIDE:
                    self.target.write(self.CHAPTER_TITLE_IMAGE % str(chapter_index))
                    self._slide_break()
                if self.args.add_chapter_illustration:
                    self.target.write(self.CHAPTER_INDEX_IMAGE % str(chapter_index))
                    self._slide_break()

            # insert group preamble if present
            if os.path.exists(os.path.join(folder, self.GROUP_INDEX_FILENAME)):
                self._append_section(folder, self.GROUP_INDEX_FILENAME)
                self._slide_break()

            # add individual sections
            for section_index, section in enumerate(group):
                if is_chapter():
                    number = self.CHAPTER_NUMBER % (chapter_index, section_index + 1)
                else:
                    number = None
                self._append_section(folder, '%s.md' % make_pathname(section), number)
                if section_index + 1 < len(group):
                    self._slide_break()

    def _slide_break(self):
        self.target.write('\n\n---\n\n')

    def _append_section(self, folder, name, headline_prefix=None):
        """
        Append a section to self.target, if headline prefix is given,
        add that to the first headline of the section.
        """

        def glossary_replace(match):
            """Get a definition of a term from the glossary."""
            name = match.group('name')
            return "_%s_" % self.glossary['terms'][name]['definition']

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
                    ''.join((line[:pos + 1], headline_prefix, line[pos + 1:])))
            for line in section:
                if self.glossary:
                    # replace definitions from glossary
                    line = self.DEFINE_PATTERN.sub(glossary_replace, line)
                self.target.write(line)
