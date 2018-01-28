#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Compile and preprocess all files so that jekyll can build a static (github) page out of it.

- copy all source files from src to docs folder
    - create front matter with title from fist header
    - remove all duplicate headers
    - inject patter number
- build an index file with all patterns
- build an index file for each group: index content: patterns + index.md
- build introduction and appendix with complete content?
- add glossary as separate file!!!

"""
import codecs
from functools import partial
import os
import re

from common import make_pathname, read_config, md_filename
from common import TITLE, FRONT_MATTER, CHAPTER_ORDER, CHAPTERS, APPENDIX, END, SKIP
from markdown_processor import MarkdownProcessor, jekyll_front_matter, prefix_headline, inject_glossary, write, remove_breaks_and_conts
from glossary import HtmlGlossaryRenderer, read_glossary


class JekyllWriter(object):
    GROUP_INDEX_IMAGE = '\n![inline,fit](img/grouped-patterns/group-%s.png)\n\n'

    def __init__(self, args):
        self.args = args
        self.source_folder = args.source
        self.target_folder = args.target
        self.config = read_config(self.args.config)
        self.glossary_renderer = HtmlGlossaryRenderer(self.args.glossary, self.args.glossary_items)
        self.glossary = read_glossary(self.args.glossary)

    def build(self):

        # TODO: add front matter
        # TODO: add index file for each chapter

        # add all the chapters
        for i, chapter in enumerate(self.config[CHAPTER_ORDER]):
            # TODO: add group indexes
            # self._append_section(chapter)

            for j, section in enumerate(self.config[CHAPTERS][chapter]):
                source_path = os.path.join(self.source_folder, make_pathname(chapter), md_filename(section))
                target_path = os.path.join(self.target_folder, md_filename(section))
                # TODO: add pattern prefix
                self._copy_file(source_path, target_path)

        # TODO: add appendix (skip glossary!!)
        # TODO: copy images (maybe in bash script?)
        # TODO: add full index
        # TODO: add full glossary        

    def _copy_file(self, source_path, target_path):
        with codecs.open(source_path, 'r', 'utf-8') as source:
            with codecs.open(target_path, 'w+', 'utf-8') as target:
                # setup the processor
                processor = MarkdownProcessor(source, filters=[
                    remove_breaks_and_conts,
                    # partial(prefix_headline, 'my headline prefix'),
                    jekyll_front_matter,
                    partial(inject_glossary, self.glossary),
                    partial(write, target),
                ])
                processor.process()
