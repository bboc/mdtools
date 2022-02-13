#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Compile and preprocess all files so that jekyll can build a static (github) page out of it.
"""
from __future__ import print_function
from __future__ import absolute_import

import codecs
from functools import partial
import logging
import html
import os

from . import common
from . import config
from . import glossary
from . import macros
from .renderer import Renderer, filters
from . import structure
from . import template
from .translate import translate as _


logger = logging.getLogger(__name__)

PREV = '◀'
UP = '▲'
NEXT = '▶'
NAVIGATION = "<a href=\"%(path)s.html\" title=\"%(link_title)s\">%(link_text)s</a>"
MOUSETRAP = """

<script type="text/javascript">
Mousetrap.bind('g n', function() {
    window.location.href = '%s.html';
    return false;
});
</script>

"""


def nav_el(link_text, path, link_title):
    """Create one navigation element."""
    link_text = html.escape(link_text)
    link_title = html.escape(link_title)
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

        # set up filters for renderer:
        self.filters = [
            partial(filters.MetadataFilter.filter, target_format=config.cfg.target_format),
            filters.remove_breaks_and_conts,
            filters.SkipOnlyFilter.filter,
            partial(filters.convert_section_links, 'html'),
            macros.MacroFilter.filter,
            glossary.get_glossary_link_processor('tooltip'),
            filters.jekyll_front_matter,
        ]

    def build(self):
        """Render the jekyll output."""

        self.configure()

        # process templates _after_ registering macros!
        template.process_templates_in_config()

        # make content pages
        current_node = structure.structure.parts[0]
        while current_node:
            logger.debug('node: "%s"' % current_node.slug)
            self._make_content_page(current_node)
            current_node = current_node.successor

    def _make_content_page(self, node):
        """Copy each section to a separate file."""
        # target_path = os.path.join(config.cfg.target, md_filename(node.relpath))
        target_path = os.path.join(config.cfg.target, common.md_filename(node.slug))

        with codecs.open(node.source_path, 'r', 'utf-8') as source:
            with codecs.open(target_path, 'w+', 'utf-8') as target:
                renderer = Renderer(source, filters=self.filters)

                renderer.add_filter(partial(filters.write, target))
                renderer.render()
                if config.cfg.read_next_navigation:
                    self._add_bottom_navigation(node, target)

    def _add_bottom_navigation(self, node, target):
        """Insert navigation for prev/up/next at the bottom of the page.

            e.g. "◀ ▲ ▶ Read next: Adapt Patterns To Context"
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
            nav.append(nav_el(PREV,
                              previous_item.slug,
                              ' '.join((_('Back to:'), previous_item.title))))

        # up: parent
        if not node.parent.is_root():
            nav.append(nav_el(UP,
                              node.parent.slug,
                              ' '.join((_('Up:'), node.parent.title))))

        next_item = node.successor
        if next_item:
            title = ' '.join((_('Read next:'), next_item.title))
            nav.append(nav_el(' '.join((NEXT, title)),
                              next_item.slug,
                              title))

        target.write(' '.join(nav))
        target.write("\n</div>\n")

        if next_item and config.cfg.read_next_shortcuts:
            target.write(MOUSETRAP % next_item.slug)
