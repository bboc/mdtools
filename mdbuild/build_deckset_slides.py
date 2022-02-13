#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Build the a slide deck in Deckset format.
"""
from __future__ import print_function
from __future__ import absolute_import

import codecs
from functools import partial

from . import config
from . import glossary
from . import macros
from .renderer import Renderer, filters
from . import structure
from . import template

from .glossary import DecksetGlossaryRenderer


class DecksetWriter(object):
    """
    Render source to one single deckset file.
    """
    def __init__(self):
        pass

    def configure(self):
        """Configure everything for the build."""

        # register all macros before processing templates
        macros.register_macro('full-glossary', partial(glossary.full_glossary_macro,
                                                       glossary.DecksetGlossaryRenderer(config.cfg.glossary_items_per_page)))
        macros.register_macro('index', macros.IndexMacro.render)
        macros.register_macro('glossary', glossary.glossary_term_macro)
        macros.register_macro('define', glossary.glossary_definition_macro)

        # set up filters for renderer:
        self.filters = [
            partial(filters.MetadataFilter.filter, target_format=None),
            filters.SkipOnlyFilter.filter,
            partial(filters.convert_section_links, 'title'),
            macros.MacroFilter.filter,
            filters.clean_images,
        ]
        # process glossary links
        if config.cfg.target_format == 'html':
            style = 'tooltip'
        else:
            style = 'plain'
        self.filters.append(glossary.get_glossary_link_processor(style))

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
        with codecs.open(config.cfg.target, 'a', 'utf-8') as target:
            current_node = structure.structure.parts[0]
            while current_node:
                self._append_content(target, current_node)
                current_node = current_node.successor

    def _append_content(self, target, node):
        """
        Append content of one node to target.
        """
        header_offset = config.cfg.header_offset + node.level - 1

        with codecs.open(node.source_path, 'r', 'utf-8') as source:
            renderer = Renderer(source, filters=self.filters)

            # processor.add_filter(partial(mdp.prefix_headline, headline_prefix))
            renderer.add_filter(partial(filters.increase_all_headline_levels, header_offset))
            renderer.add_filter(partial(filters.write, target))

            renderer.render()
        target.write('\n\n---\n\n')
