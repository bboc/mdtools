#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Compile and preprocess all files so that jekyll can build a static (github) page out of it.
"""
from __future__ import print_function
from __future__ import absolute_import

import codecs
from functools import partial
import os

from .common import md_filename
from . import glossary
from . import macros
from . import markdown_processor as mdp
from . import template

PREV_ELEMENT = "[&#9664; %(name)s](%(path)s.html)"
UP_ELEMENT = "[&#9650; %(name)s](%(path)s.html)"
NEXT_ELEMENT = "[&#9654; %(name)s](%(path)s.html)"


def nav_el(target, template, item):
    target.write(template % dict(name=item.title, path=item.slug))


class JekyllWriter(object):
    GROUP_INDEX_IMAGE = '\n![inline,fit](img/grouped-patterns/group-%s.png)\n\n'

    def __init__(self, config, structure):
        self.cfg = config
        self.structure = structure

    def build(self):
        """Render the jekyll output.
        """
        # register all macros before processing templates
        macros.register_macro('full-glossary', partial(glossary.glossary_macro, glossary.JekyllGlossaryRenderer(9999)))
        macros.register_macro('index', partial(macros.IndexMacro.render, self.structure, 'html'))

        template.process_templates_in_config(self.cfg)
        self.make_content_pages()

    def make_content_pages(self):
        current_node = self.structure.children[0]
        while current_node:
            self._make_content_page(current_node)
            current_node = current_node.successor

    def common_filters(self):
        """Return the set of filters common to all pipelines."""
        return [
            mdp.remove_breaks_and_conts,
            partial(mdp.convert_section_links, mdp.SECTION_LINK_TO_HMTL),
            partial(mdp.inject_glossary),
            partial(macros.MacroFilter.filter),
            partial(mdp.add_glossary_term_tooltips, mdp.GLOSSARY_TERM_TOOLTIP_TEMPLATE),
        ]

    def _make_content_page(self, node):
        """Copy each section to a separate file."""
        # target_path = os.path.join(self.cfg.target, md_filename(node.relpath))
        target_path = os.path.join(self.cfg.target, md_filename(node.slug))

        with codecs.open(node.source_path, 'r', 'utf-8') as source:
            with codecs.open(target_path, 'w+', 'utf-8') as target:
                processor = mdp.MarkdownProcessor(source, filters=self.common_filters())
                processor.add_filter(mdp.jekyll_front_matter)
                # processor.add_filter(partial(mdp.prefix_headline, headline_prefix))
                processor.add_filter(partial(mdp.summary_tags, mode=mdp.STRIP_MODE))
                processor.add_filter(partial(mdp.write, target))
                processor.process()
                self._add_navigation(node, target)

    def _add_navigation(self, node, target):
        """Insert navigation for prev/up/next at the bottom of the page."""
        target.write("\n\n")

        next_item = node.successor
        if next_item:
            nav_el(target, NEXT_ELEMENT, next_item)
            target.write("<br/>")

        previous_item = node.predecessor
        if not node.parent.is_root():
            parent_item = node.parent
        else:
            parent_item = None

        # Skip previous if it is the parent item
        if previous_item and previous_item is not parent_item:
            nav_el(target, PREV_ELEMENT, previous_item)
            target.write("<br/>")

        # up: parent
        if not node.parent.is_root():
            nav_el(target, UP_ELEMENT, node.parent)
        target.write("\n\n")
