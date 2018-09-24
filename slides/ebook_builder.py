#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Compile all files so that they can be rendered to LaTEX and ePub.
"""

import codecs
from functools import partial
import os

from common import make_headline_prefix
from config import get_config, CONTENT
import markdown_processor as mdp
from glossary import EbookGlossaryRenderer, read_glossary


class EbookWriter(object):
    GROUP_INDEX_IMAGE = '\n![inline,fit](img/grouped-patterns/group-%s.png)\n\n'

    def __init__(self, args):
        self.args = args
        self.source_folder = args.source
        self.target_folder = args.target
        self.config = get_config(self.args.config)
        self.glossary_renderer = EbookGlossaryRenderer(self.args.glossary, 9999)
        self.glossary = read_glossary(self.args.glossary)

    def build(self):
        """Build three files: intro/patterns/appendix."""
        content = self.config[CONTENT]
        # build introduction

        def build_intro_and_appendix(filename, part):
            target_path = os.path.join(self.target_folder, filename)
            with codecs.open(target_path, 'w+', 'utf-8') as target:
                for item in part.sections:
                    self._append_section(target, part, item)

        build_intro_and_appendix('tmp-introduction.md', content.introduction)

        # build all the chapters/sections
        target_path = os.path.join(self.target_folder, 'tmp-chapters.md')
        with codecs.open(target_path, 'w+', 'utf-8') as target:
            for chapter in content.chapters:
                self._build_chapter_index(target, chapter)
                for section in chapter.sections:
                    self._append_section(target,
                                         chapter,
                                         section,
                                         headline_level_increase=1,
                                         headline_prefix=make_headline_prefix(self.args, self.config, chapter.id, section.id))

        # finally build appendix
        build_intro_and_appendix('tmp-appendix.md', content.appendix)

    def common_filters(self):
        """Return the set of filters common to all pipelines."""
        return [
            mdp.remove_breaks_and_conts,
            partial(mdp.convert_section_links, mdp.SECTION_LINK_TITLE_ONLY),
            partial(mdp.inject_glossary, self.glossary),
            partial(mdp.glossary_tooltip, self.glossary, mdp.GLOSSARY_TERM_PLAIN_TEMPLATE),
            mdp.clean_images,
        ]

    def _append_section(self, target, chapter, section, headline_level_increase=0, headline_prefix=None):
        """Append each section to self.target."""
        source_path = os.path.join(self.source_folder, chapter.slug, section.md_filename())
        with codecs.open(source_path, 'r', 'utf-8') as source:
            processor = mdp.MarkdownProcessor(source, filters=self.common_filters())
            processor.add_filter(partial(mdp.prefix_headline, headline_prefix))
            processor.add_filter(partial(mdp.increase_all_headline_levels, headline_level_increase))
            processor.add_filter(partial(mdp.insert_glossary, self.glossary_renderer))
            processor.add_filter(partial(mdp.write, target))
            processor.process()
        target.write("\n\n")

    def _build_chapter_index(self, target, chapter):
        """Add chapter headline, and index.md if present."""

        target.write('\n')
        target.write('## %s \n' % chapter.title)
        target.write('\n')
        # this image is not rendered directly under the headline, so it makes no sense to have this
        # target.write('\n![](img/pattern-groups/group-%s.png)\n\n' % chapter.id)
        chapter_index_file = os.path.join(self.source_folder, chapter.slug, 'index.md')
        if os.path.exists(chapter_index_file):
            with codecs.open(chapter_index_file, 'r', 'utf-8') as cif:
                cif.next()  # skip headline
                processor = mdp.MarkdownProcessor(cif, filters=self.common_filters())
                processor.add_filter(partial(mdp.write, target))
                processor.process()
            target.write('\n')
