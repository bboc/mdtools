#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Build a slide deck (either in Deckset format or as reveal.js.
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import

import codecs
import os
import re
from shutil import copyfile

from .common import create_directory, md_filename
from . import translate

from .build_deckset_slides import DecksetWriter
from .build_revealjs_slides import RevealJsWriter, RevealJSBuilder
from .build_web_content import cmd_convert_to_web
from .revealjs_converter import RevealJsHtmlConverter

TMP_FOLDER = 'tmp-groups'

# TODO: this needs to go somewhere else
translate.read_translation_memory('content/localization.po')


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
    content = get_config(args.config)[CONTENT]

    def make_group(group):
        # create group dir
        group_root = os.path.join(args.target, group.slug)
        create_directory(group_root)
        # create group index file
        make_file(group_root, "index", group.title, '#')
        # create individual sections (add section name as headline)
        for section in group.sections:
            make_file(group_root, section, section, '##')

    def make_file(root, filename_root, title_root, markup='#'):
        """Create file if it does not exist."""
        filename = os.path.join(root, md_filename(filename_root))
        if not os.path.exists(filename):
            with codecs.open(filename, 'w+', 'utf-8') as fp:
                fp.write('%s %s\n\n' % (markup, make_title(title_root)))
        else:
            if args.verbose:
                print("skipped %s" % title_root)

    make_file(args.target, content.title, content.title)
    if content.introduction:
        make_group(content.introduction)
    for chapter in content.chapters:
        make_group(chapter)
    if content.appendix:
        make_group(content.appendix)
    if content.end:
        make_file(args.target, content.end, content.end)


class SectionCompiler(object):
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
        content = self.config[CONTENT]
        if content.title:
            self._copy_file(md_filename(content.title))
        if content.introduction:
            self._compile_section_group(content.introduction)

            # insert illustrations for all chapters between intro and chapters
            if self.args.add_chapter_illustration:
                for chapter in content['chapters']:
                    self.target.write(self.GROUP_INDEX_IMAGE % str(chapter.id))
                    self._append_section_break()
        for chapter in content.chapters:
                self._compile_section_group(chapter)
        if content.appendix:
            self._compile_section_group(content.appendix)
        if content.end:
            self._copy_file(md_filename(content.end))

    def _copy_file(self, name):
        copyfile(os.path.join(self.source, name), os.path.join(self.target_folder, name))

    def _compile_section_group(self, group):
        """Compile front matter, chapters and appendix."""
        folder = os.path.join(self.source, group.slug)

        with codecs.open(os.path.join(self.target_folder, group.md_filename()), 'w+', 'utf-8') as self.target:
            if group.is_chapter():
                # chapter title and index slides
                if self.INSERT_CHAPTER_TEXT_TITLE_SLIDE:
                    self.target.write('\n# %s. %s' % (group.id, group.title))
                    self._slide_break()
                if self.INSERT_CHAPTER_IMG_TITLE_SLIDE:
                    self.target.write(self.CHAPTER_TITLE_IMAGE % str(group.id))
                    self._slide_break()
                if self.args.add_chapter_illustration:
                    self.target.write(self.CHAPTER_INDEX_IMAGE % str(group.id))
                    self._slide_break()

            # insert group preamble if present
            if os.path.exists(os.path.join(folder, self.GROUP_INDEX_FILENAME)):
                self._append_section(folder, self.GROUP_INDEX_FILENAME)
                self._slide_break()

            # add individual sections
            for section in group.sections:
                if group.is_chapter() and self.args.section_prefix:
                    headline_prefix = self.args.section_prefix % dict(chapter=group.id, section=section.id)
                else:
                    headline_prefix = None
                self._append_section(folder, section.md_filename(), headline_prefix)
                if section.id < len(group.sections):
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
                line = next(section)
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
