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

        # add all the chapters
        for chapter in self.index['groups']:
            self._build_chapter_index(chapter)
            for section in self.index['patterns-by-group'][chapter['path']]:
                self._copy_section(chapter['path'][:-3],
                                   section['path'],
                                   make_headline_prefix(self.args, self.config, chapter['gid'], section['pid']))

        self._compile_front_matter()
        self._copy_appendix()
        self._build_index()
        self._build_glossary()

    def _build_glossary(self):
        with codecs.open(os.path.join(self.target_folder, md_filename("glossary")), 'w+', 'utf-8') as target:
            self.glossary_renderer.render(target.write)

    def _build_index(self):
        """Build site index with from template. Already translation-aware."""
        with codecs.open(self.args.template, 'r', 'utf-8') as source:
            with codecs.open(os.path.join(self.target_folder, md_filename("index")), 'w+', 'utf-8') as target:
                processor = mdp.MarkdownProcessor(source, filters=[
                    partial(mdp.insert_index, '<!-- GROUP-INDEX -->', self.index['groups']),
                    partial(mdp.insert_index, '<!-- PATTERN-INDEX -->', self.index['patterns']),
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
                print chapter_index_file
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

    def _compile_front_matter(self):
        with codecs.open(os.path.join(self.target_folder, md_filename(FRONT_MATTER)), 'w+', 'utf-8') as target:
            target.write(mdp.FRONT_MATTER_SEPARATOR)
            target.write(mdp.FRONT_MATTER_TITLE % FRONT_MATTER.title())
            target.write(mdp.FRONT_MATTER_SEPARATOR)
            target.write('\n')
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

    def _copy_appendix(self):
        """Copy all files in the appendix to individual files (skip glossary)."""
        for item in self.config[APPENDIX]:
            if item not in ['glossary', 'authors']:
                self._copy_section(APPENDIX, md_filename(item), '')

    def _copy_section(self, chapter_path, section_path, headline_prefix):
        """Copy each section to a separate file."""
        source_path = os.path.join(self.source_folder, chapter_path, section_path)
        target_path = os.path.join(self.target_folder, section_path)
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
