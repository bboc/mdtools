#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Compile and preprocess all files so that jekyll can build a static (github) page out of it.
"""

import codecs
from functools import partial
import os
from textwrap import dedent

from common import make_pathname, read_config, md_filename, make_headline_prefix
from common import TITLE, FRONT_MATTER, CHAPTER_ORDER, CHAPTERS, APPENDIX, END, SKIP
from index import read_index_db
import markdown_processor as mdp
from glossary import JekyllGlossaryRenderer, read_glossary

CHAPTER_INDEX = dedent("""
---
title: <!-- CHAPTER-NAME -->
---

<!-- CHAPTER-INTRO -->

<!-- SECTION-INDEX -->

""")


PREV_ELEMENT = "[&#9664; %(name)s](%(path)s.html)"
UP_ELEMENT = "[&#9650; %(name)s](%(path)s.html)"
NEXT_ELEMENT = "[&#9654; %(name)s](%(path)s.html)"


class JekyllWriter(object):
    GROUP_INDEX_IMAGE = '\n![inline,fit](img/grouped-patterns/group-%s.png)\n\n'

    def __init__(self, args):
        self.args = args
        self.source_folder = args.source
        self.target_folder = args.target
        self.config = read_config(self.args.config)
        self.glossary_renderer = JekyllGlossaryRenderer(self.args.glossary, 9999)
        self.glossary = read_glossary(self.args.glossary)
        self.index = read_index_db(self.args.index)

    def build(self):

        self._build_site_index()
        self._build_section_index()
        self._compile_front_matter()
        self._build_glossary()
        self._copy_appendix()

        # add all the chapters/sections
        for chapter in self.index['groups']:
            self._build_chapter_index(chapter)
            for section in self.index['patterns-by-group'][chapter['path']]:
                self._copy_section(chapter,
                                   section,
                                   make_headline_prefix(self.args, self.config, chapter['gid'], section['pid']))

    def _build_site_index(self):
        """Build site index from template. Already translation-aware."""
        with codecs.open(self.args.template, 'r', 'utf-8') as source:
            with codecs.open(os.path.join(self.target_folder, md_filename("index")), 'w+', 'utf-8') as target:
                processor = mdp.MarkdownProcessor(source, filters=[
                    partial(mdp.insert_index, '<!-- GROUP-INDEX -->', self.index['groups']),
                    partial(mdp.write, target),
                ])
                processor.process()

    def _build_section_index(self):
        """Build index of all sections from template. Already translation-aware."""
        # TODO: remove hardcoded path
        with codecs.open("content/website/_templates/pattern-index.md", 'r', 'utf-8') as source:
            with codecs.open(os.path.join(self.target_folder, md_filename("pattern-index")), 'w+', 'utf-8') as target:
                processor = mdp.MarkdownProcessor(source, filters=[
                    partial(mdp.insert_index, '<!-- PATTERN-INDEX -->', self.index['patterns'], sort=True),
                    partial(mdp.write, target),
                ])
                processor.process()

    def _build_chapter_index(self, chapter):
        with codecs.open(os.path.join(self.target_folder, chapter['path']), 'w+', 'utf-8') as target:
            target.write(mdp.FRONT_MATTER_SEPARATOR)
            target.write(mdp.FRONT_MATTER_TITLE % chapter['name'])
            target.write(mdp.FRONT_MATTER_SEPARATOR)
            target.write('\n')

            # copy in chapter index
            chapter_index_file = os.path.join(self.source_folder, chapter['path'][:-3], 'index.md')
            if os.path.exists(chapter_index_file):
                with codecs.open(chapter_index_file, 'r', 'utf-8') as cif:
                    cif.next()  # skip headline
                    processor = mdp.MarkdownProcessor(cif, filters=[
                        mdp.remove_breaks_and_conts,
                        partial(mdp.inject_glossary, self.glossary),
                        partial(mdp.write, target),
                    ])
                    processor.process()
                target.write('\n')

            # build section index
            for section in self.index['patterns-by-group'][chapter['path']]:
                target.write(mdp.INDEX_ELEMENT % dict(name=section['name'],
                                                      path=section['path'][:-3]))
            self.chapter_navigation(target, chapter)

    def _compile_front_matter(self):
        with codecs.open(os.path.join(self.target_folder, md_filename(FRONT_MATTER)), 'w+', 'utf-8') as target:
            with codecs.open("content/website/_templates/introduction.md", 'r', 'utf-8') as template:
                for line in template:
                    target.write(line)

            for item in self.config[FRONT_MATTER]:
                source_path = os.path.join(self.source_folder, FRONT_MATTER, md_filename(item))
                with codecs.open(source_path, 'r', 'utf-8') as source:
                    processor = mdp.MarkdownProcessor(source, filters=[
                        mdp.remove_breaks_and_conts,
                        partial(mdp.inject_glossary, self.glossary),
                        partial(mdp.write, target),
                    ])
                    processor.process()
                target.write('\n')
            self.intro_navigation(target)

    def _build_glossary(self):
        with codecs.open(os.path.join(self.target_folder, md_filename("glossary")), 'w+', 'utf-8') as target:
            self.glossary_renderer.render(target.write)

    def _copy_appendix(self):
        """Copy all files in the appendix to individual files (skip glossary)."""
        for item in self.config[APPENDIX]:
            if item not in ['glossary', 'authors']:
                self._copy_appendix_section(md_filename(item))

    def _copy_appendix_section(self, section_path):
        """Copy each section to a separate file."""
        source_path = os.path.join(self.source_folder, APPENDIX, section_path)
        target_path = os.path.join(self.target_folder, section_path)
        with codecs.open(source_path, 'r', 'utf-8') as source:
            with codecs.open(target_path, 'w+', 'utf-8') as target:
                processor = mdp.MarkdownProcessor(source, filters=[
                    mdp.remove_breaks_and_conts,
                    mdp.jekyll_front_matter,
                    partial(mdp.write, target),
                ])
                processor.process()

    def _copy_section(self, chapter, section, headline_prefix):
        """Copy each section to a separate file."""
        source_path = os.path.join(self.source_folder, chapter['path'][:-3], section['path'])
        target_path = os.path.join(self.target_folder, section['path'])
        with codecs.open(source_path, 'r', 'utf-8') as source:
            with codecs.open(target_path, 'w+', 'utf-8') as target:
                processor = mdp.MarkdownProcessor(source, filters=[
                    mdp.remove_breaks_and_conts,
                    # partial(mdp.prefix_headline, headline_prefix),
                    mdp.jekyll_front_matter,
                    partial(mdp.inject_glossary, self.glossary),
                    partial(mdp.write, target),
                ])
                processor.process()
                self.section_navigation(target, chapter, section)

    def section_navigation(self, target, chapter, section):
        """Insert prev/up/next."""
        target.write("\n\n")
        patterns = self.index['patterns-by-group'][chapter['path']]

        # next link: next pattern, next group, or first group
        if section['pid'] == len(patterns):
            if section['gid'] == len(self.index['groups']):
                item = self.index['groups-by-gid'][1]
            else:
                item = self.index['groups-by-gid'][section['pid'] - 2]
        else:
            item = patterns[(section['pid'])]
        nav_el(target, NEXT_ELEMENT, item)
        target.write("<br/>")
        # prev link = prev pattern or ???
        if section['pid'] > 1:
            p_next = patterns[(section['pid'] - 2)]
            nav_el(target, PREV_ELEMENT, p_next)
            target.write("<br/>")
        # up: group index
        group = self.index['groups-by-gid'][section['gid']]
        nav_el(target, UP_ELEMENT, group)
        target.write("\n\n")

    def chapter_navigation(self, target, chapter):
        """Insert prev/next."""
        target.write("\n\n")

        # next link: always first pattern in group
        item = self.index['patterns-by-group'][chapter['path']][0]
        nav_el(target, NEXT_ELEMENT, item)
        target.write("<br/>")
        # back:
        if chapter['gid'] > 1:
            # last pattern of previous group
            target_group = self.index['groups'][(chapter['gid'] - 2)]
        else:
            # last pattern of last group
            target_group = self.index['groups'][-1]
        item = self.index['patterns-by-group'][target_group['path']][-1]
        nav_el(target, PREV_ELEMENT, item)
        target.write("\n\n")

    def intro_navigation(self, target):
        """Link to first group"""
        target.write("\n\n")
        item = self.index['groups-by-gid'][1]
        nav_el(target, NEXT_ELEMENT, item)

        target.write("\n\n")


def nav_el(target, template, item):
    target.write(template % dict(name=item['name'], path=item['path'][:-3]))
