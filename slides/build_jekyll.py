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
            # self._build_chapter_index(cidx, chapter)
            for section in self.index['patterns-by-group'][chapter['path']]:
                source_path = os.path.join(self.source_folder, chapter['path'][:-3], section['path'])
                target_path = os.path.join(self.target_folder, section['path'])
                self._copy_file(source_path,
                                target_path,
                                make_headline_prefix(self.args, self.config, chapter['gid'], section['pid']))

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

    def _build_chapter_index(self):
        pass

    def _compile_section(sef):
        pass

    def _copy_file(self, source_path, target_path, headline_prefix):
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
