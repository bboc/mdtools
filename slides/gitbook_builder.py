#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Build a gitbook from source files:

- create summary from structure.yaml
- copy all files and update illustaration links
- anything else?

"""

import codecs
from functools import partial
import os

from common import read_config, md_filename, make_headline_prefix
from common import FRONT_MATTER, APPENDIX
from index import read_index_db
import markdown_processor as mdp
from glossary import EbookGlossaryRenderer, read_glossary


class GitbookBuilder(object):

    def __init__(self, args):
        self.args = args
        self.source_folder = args.source
        self.target_folder = args.target
        self.config = read_config(self.args.config)
        self.glossary_renderer = EbookGlossaryRenderer(self.args.glossary, 9999)
        self.glossary = read_glossary(self.args.glossary)
        self.index = read_index_db(self.args.index)

    def build(self):
        """Build three files: intro/patterns/appendix."""

        # build introduction
        # target_path = os.path.join(self.target_folder, 'tmp-introduction.md')
        # with codecs.open(target_path, 'w+', 'utf-8') as target:
        #     for item in self.config[FRONT_MATTER]:
        #         self._append_section(target, FRONT_MATTER, md_filename(item))

        # # build all the chapters/sections
        # target_path = os.path.join(self.target_folder, 'tmp-chapters.md')
        # with codecs.open(target_path, 'w+', 'utf-8') as target:
        #     for chapter in self.index['groups']:
        #         self._build_chapter_index(target, chapter)
        #         for section in self.index['patterns-by-group'][chapter['path']]:
        #             self._append_section(target,
        #                                  chapter['path'][:-3],
        #                                  section['path'],
        #                                  headline_level_increase=1,
        #                                  headline_prefix=make_headline_prefix(self.args, self.config, chapter['gid'], section['pid']))

        # # finally build appendix
        # target_path = os.path.join(self.target_folder, 'tmp-appendix.md')
        # with codecs.open(target_path, 'w+', 'utf-8') as target:
        #     for item in self.config[APPENDIX]:
        #             self._append_section(target, APPENDIX, md_filename(item))

    def _append_section(self, target, chapter, section, headline_level_increase=0, headline_prefix=None):
        """Append each section to self.target."""
        # source_path = os.path.join(self.source_folder, chapter, section)
        # with codecs.open(source_path, 'r', 'utf-8') as source:
        #         processor = mdp.MarkdownProcessor(source, filters=[
        #             mdp.remove_breaks_and_conts,
        #             partial(mdp.prefix_headline, headline_prefix),
        #             partial(mdp.increase_all_headline_levels, headline_level_increase),
        #             partial(mdp.insert_glossary, self.glossary_renderer),
        #             mdp.clean_images,
        #             partial(mdp.inject_glossary, self.glossary),
        #             partial(mdp.write, target),
        #         ])
        #         processor.process()
        # target.write("\n\n")

    def _build_summary(self, target, chapter):
        """Add chapter headline, and index.md if present."""
        print repr(self.index)

        # target.write('\n')
        # target.write('## %s \n' % chapter['name'])
        # target.write('\n')
        # # this image is not rendered directly under the headline, so it makes no sense to have this
        # # target.write('\n![](img/pattern-groups/group-%s.png)\n\n' % chapter['gid'])
        # chapter_index_file = os.path.join(self.source_folder, chapter['path'][:-3], 'index.md')
        # if os.path.exists(chapter_index_file):
        #     with codecs.open(chapter_index_file, 'r', 'utf-8') as cif:
        #         cif.next()  # skip headline
        #         processor = mdp.MarkdownProcessor(cif, filters=[
        #             mdp.remove_breaks_and_conts,
        #             partial(mdp.inject_glossary, self.glossary),
        #             mdp.clean_images,
        #             partial(mdp.write, target),
        #         ])
        #         processor.process()
        #     target.write('\n')
