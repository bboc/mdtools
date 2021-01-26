# -*- coding: utf-8 -*-
"""
Compile all files into one file so that they can be rendered to LaTEX and ePub.
"""
from __future__ import print_function
from __future__ import absolute_import

import codecs
from functools import partial
import os

from .glossary_processor import get_glossary_processor

from . import config
from . import glossary
from . import macros
from . import markdown_processor as mdp
from . import structure
from . import template

class EbookWriter(object):

    def __init__(self):
        # self.glossary_renderer = EbookGlossaryRenderer(self.args.glossary,)
        # self.gp = get_glossary_processor(args.glossary_style, self.glossary)
        pass

    def build(self):
        """
        Add all documents into one target file.
        """
        # register all macros before processing templates
        macros.register_macro('full-glossary', partial(glossary.glossary_macro, glossary.EbookGlossaryRenderer()))
        macros.register_macro('index', macros.IndexMacro.render),
        template.process_templates_in_config()

        # start by copying the main template
        template.template('default', config.cfg.template, config.cfg.target)

        # then append all the content pages

        with codecs.open(config.cfg.target, 'w+', 'utf-8') as target:
            current_node = structure.structure.children[0]
            while current_node:
                self._append_content(target, current_node)
                current_node = current_node.successor

    def build_old(self):
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
        with codecs.open(target_path, 'a', 'utf-8') as target:
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

        # emit glossary stuff into tmp-appendix.md if necessary
        with codecs.open(os.path.join(self.target_folder, 'tmp-appendix.md'), 'a', 'utf-8') as target:
            self.gp.glossary_post_processing(target)

    def _append_content(self, target, node, headline_level_increase=0, headline_prefix=None):
        """Append each section to target."""
        with codecs.open(node.source_path, 'r', 'utf-8') as source:
            processor = mdp.MarkdownProcessor(source, filters=[
                mdp.remove_breaks_and_conts,
                partial(mdp.convert_section_links, mdp.SECTION_LINK_TITLE_ONLY),
                mdp.inject_glossary,
                macros.MacroFilter.filter,

                # TODO: this needs to be configurable
                # self.gp.replace_glossary_references,
                partial(mdp.summary_tags, mode=mdp.STRIP_MODE),
                mdp.clean_images,
                partial(mdp.prefix_headline, headline_prefix),
                partial(mdp.increase_all_headline_levels, headline_level_increase),
                partial(mdp.write, target),
            ])
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
                next(cif)  # skip headline
                processor = mdp.MarkdownProcessor(cif, filters=self.common_filters())
                processor.add_filter(partial(mdp.write, target))
                processor.process()
            target.write('\n\n')
