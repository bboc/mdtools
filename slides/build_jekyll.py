#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Compile and preprocess all files so that jekyll can build a static (github) page out of it.

- inject patter number
- build an index file with all patterns
- build an index file for each group: index content: patterns + index.md
- build introduction and appendix with complete content?
- add glossary as separate file!!!

"""
import codecs
from functools import partial
import os
from textwrap import dedent

from common import make_pathname, read_config, md_filename, make_headline_prefix
from common import TITLE, FRONT_MATTER, CHAPTER_ORDER, CHAPTERS, APPENDIX, END, SKIP
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

    def build(self):

        # TODO: add front matter
        # TODO: add index file for each chapter
        index = read_config(self.args.index)

        # add all the chapters
        for cidx, chapter in enumerate(self.config[CHAPTER_ORDER]):
            # TODO: add group indexes
            # self._build_chapter_index(cidx, chapter)

            for sidx, section in enumerate(self.config[CHAPTERS][chapter]):
                source_path = os.path.join(self.source_folder, make_pathname(chapter), md_filename(section))
                target_path = os.path.join(self.target_folder, md_filename(section))
                self._copy_file(source_path, target_path, make_headline_prefix(self.args, self.config, cidx + 1, sidx + 1))

        # TODO: add appendix (skip glossary!!)
        # TODO: add full index
        self._build_index(index)
        # TODO: add full glossary
        with codecs.open(os.path.join(self.target_folder, md_filename("glossary")), 'w+', 'utf-8') as target:
            self.glossary_renderer.render(target.write)

    def _build_index(self, index):
        print self.args.template
        with codecs.open(self.args.template, 'r', 'utf-8') as source:
            with codecs.open(os.path.join(self.target_folder, md_filename("index")), 'w+', 'utf-8') as target:
                processor = mdp.MarkdownProcessor(source, filters=[
                    partial(mdp.insert_index, '<!-- GROUP-INDEX -->', index['groups']),
                    partial(mdp.insert_index, '<!-- PATTERN-INDEX -->', index['patterns']),
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
