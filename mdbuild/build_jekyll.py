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
from . import config
from . import glossary
from . import macros
from . import markdown_processor as mdp
from . import structure
from . import template
from .translate import translate as _


PREV = '&#9664;'
UP = '&#9650;'
NEXT = '&#9654;'
NAVIGATION = "<a href=\"%(path)s.html\" title=\"%(alt_title)s\">%(title)s</a>"


def nav_el(title, path, alt_title):
    """Create one navigation element."""
    return NAVIGATION % locals()


class JekyllWriter(object):

    def __init__(self):
        pass

    def configure(self):
        """Configure everything for the build."""
        # register all macros before processing templates
        macros.register_macro('full-glossary', partial(glossary.full_glossary_macro, glossary.JekyllGlossaryRenderer()))
        macros.register_macro('index', macros.IndexMacro.render)
        macros.register_macro('glossary', glossary.glossary_term_macro)
        macros.register_macro('define', glossary.glossary_definition_macro)
        macros.register_macro('html-menu', macros.MenuMacro.render)

        # set up filters for markdown processor:
        self.filters = [
            mdp.remove_breaks_and_conts,
            partial(mdp.convert_section_links, mdp.SECTION_LINK_TO_HMTL),
            macros.MacroFilter.filter,
            glossary.get_glossary_link_processor('tooltip'),
            mdp.jekyll_front_matter,
            partial(mdp.summary_tags, mode=mdp.STRIP_MODE),
        ]

    def build(self):
        """Render the jekyll output."""

        self.configure()

        # process templates _after_ registering macros!
        template.process_templates_in_config()

        # make content pages
        current_node = structure.structure.parts[0]
        while current_node:
            self._make_content_page(current_node)
            current_node = current_node.successor

    def _make_content_page(self, node):
        """Copy each section to a separate file."""
        # target_path = os.path.join(config.cfg.target, md_filename(node.relpath))
        target_path = os.path.join(config.cfg.target, md_filename(node.slug))

        with codecs.open(node.source_path, 'r', 'utf-8') as source:
            with codecs.open(target_path, 'w+', 'utf-8') as target:
                processor = mdp.MarkdownProcessor(source, filters=self.filters)

                processor.add_filter(partial(mdp.write, target))
                processor.process()
                self._add_bottom_navigation(node, target)

    def _add_bottom_navigation(self, node, target):
        """Insert navigation for prev/up/next at the bottom of the page.

            e.g. "◀ ▲ ▶ Adapt Patterns To Context"
        """
        target.write('\n\n<div class="bottom-nav">\n')

        nav = []

        previous_item = node.predecessor
        if not node.parent.is_root():
            parent_item = node.parent
        else:
            parent_item = None

        # Skip previous if it is the parent item
        if previous_item and previous_item is not parent_item:
            nav.append(nav_el(PREV, previous_item.slug,
                       ' '.join((_('back to:'), previous_item.title))))

        # up: parent
        if not node.parent.is_root():
            nav.append(nav_el(UP, node.parent.slug,
                       ' '.join((_('up:'), node.parent.title))))

        next_item = node.successor
        if next_item:
            nav.append(nav_el(' '.join((NEXT, _('read next:'), next_item.title)),
                       next_item.slug, ''))

        target.write(' '.join(nav))
        target.write("\n</div>\n")
