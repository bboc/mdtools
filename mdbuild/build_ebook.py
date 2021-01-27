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
        pass

    def configure(self):
        """Configure everything for the build."""

        # register all macros before processing templates
        macros.register_macro('full-glossary', partial(glossary.full_glossary_macro, glossary.EbookGlossaryRenderer()))
        macros.register_macro('index', macros.IndexMacro.render)
        macros.register_macro('glossary', glossary.glossary_term_macro)
        macros.register_macro('define', glossary.glossary_definition_macro)

        # set up filters for markdown processor:
        self.filters = [
            mdp.remove_breaks_and_conts,
            partial(mdp.convert_section_links, mdp.SECTION_LINK_TITLE_ONLY),
            macros.MacroFilter.filter,
            partial(mdp.summary_tags, mode=mdp.STRIP_MODE),
            mdp.clean_images,
        ]
        # add a filter dependent on output format
        if config.cfg.target_format == 'html':
            self.filters.append(partial(mdp.add_glossary_term_tooltips, mdp.GLOSSARY_TERM_TOOLTIP_TEMPLATE))
            self.filters.append(partial(mdp.add_glossary_term_tooltips, mdp.GLOSSARY_TERM_TOOLTIP_TEMPLATE))
        else:
            gp = get_glossary_processor('plain')
            self.filters.append(gp.replace_glossary_references)

    def build(self):
        """
        Add all documents into one target file.
        """

        self.configure()

        # process templates _after_ registering macros!
        template.process_templates_in_config()

        # start by copying the main template
        if config.cfg.template:
            template.template('default', config.cfg.template, config.cfg.target)
        else:
            # truncate file if it exists
            with open(config.cfg.target, 'w'):
                pass

        # then append all the content pages
        with codecs.open(config.cfg.target, 'w+', 'utf-8') as target:
            current_node = structure.structure.children[0]
            while current_node:
                self._append_content(target, current_node)
                current_node = current_node.successor

    def _append_content(self, target, node, headline_level_increase=0, headline_prefix=None):
        """
        Append each section to target.
        # TODO: calculate headline level increase and
            potentially headline level,
            is that dependent on output format??
        """
        with codecs.open(node.source_path, 'r', 'utf-8') as source:
            processor = mdp.MarkdownProcessor(source, filters=self.filters)

            processor.add_filter(partial(mdp.prefix_headline, headline_prefix))
            processor.add_filter(partial(mdp.increase_all_headline_levels, headline_level_increase))
            processor.add_filter(partial(mdp.write, target))

            processor.process()
        target.write("\n\n")
