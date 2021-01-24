#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Compile and preprocess all files so that jekyll can build a static (github) page out of it.
"""
from __future__ import print_function
from __future__ import absolute_import

import codecs
from collections import defaultdict
from functools import partial
import os
import sys
import shutil
from textwrap import dedent

from .common import md_filename
from . import markdown_processor as mdp
from . import glossary
from . import macros

CHAPTER_INDEX_TEMPLATE = dedent("""
---
title: <!-- CHAPTER-NAME -->
---

<!-- CHAPTER-INTRO -->

<!-- SECTION-INDEX -->

""")


PREV_ELEMENT = "[&#9664; %(name)s](%(path)s.html)"
UP_ELEMENT = "[&#9650; %(name)s](%(path)s.html)"
NEXT_ELEMENT = "[&#9654; %(name)s](%(path)s.html)"


def nav_el(target, template, item):
    target.write(template % dict(name=item.title, path=item.slug))


class JekyllWriter(object):
    GROUP_INDEX_IMAGE = '\n![inline,fit](img/grouped-patterns/group-%s.png)\n\n'

    def __init__(self, config, structure):
        self.cfg = config
        self.source_folder = self.cfg.source
        self.target_folder = self.cfg.target
        self.structure = structure
        self.glossary_renderer = glossary.JekyllGlossaryRenderer(9999)
        self.summary_db = defaultdict(list)

        # register all macros here
        macros.register_macro('full-glossary', partial(glossary.glossary_macro, glossary.JekyllGlossaryRenderer(9999)))
        macros.register_macro('index', partial(macros.IndexMacro.render, self.structure, 'html'))

    def build(self):
        """Render the jekyll output.
        """
        self.copy_templates()         
        self.make_content_pages()

    def make_content_pages(self):
        current_node = self.structure.children[0]
        while current_node:
            self._make_content_page(current_node)
            current_node = current_node.successor

    def copy_templates(self):
        """
        Copy templates to destination.

        template processing has 3 modes:
        - default: substitute variables and translations
        - copy: simply copy, don't touch
        - markdown: full markdown processing (inkl. jekyll front matter and macros)
        """
        for t in self.cfg.templates:
            try:
                mode = t.mode
            except AttributeError:
                mode = 'default'
            try:
                t.source
            except AttributeError:
                print('ERROR: template has no source')
                sys.exit(1)
            try:
                t.destination
            except AttributeError:
                print('ERROR: no destination for template', t.source)
                sys.exit(1)

            if mode == 'copy':
                shutil.copy(t.source, t.destination)
            elif mode == 'markdown':
                self._markdown_template(t)
            elif mode == 'default':
                self._default_template(t)
            else:
                print("ERROR: unknown mode ", mode, 'for template', t.source)
                sys.exit(1)

    def _markdown_template(self, template):
        """Run the template through most of the markdown filters."""

        with codecs.open(template.source, 'r', 'utf-8') as source:
            with codecs.open(template.destination, 'w+', 'utf-8') as target:
                processor = mdp.MarkdownProcessor(source, filters=[

                    partial(mdp.convert_section_links, mdp.SECTION_LINK_TO_HMTL),
                    partial(mdp.inject_glossary),
                    partial(macros.MacroFilter.filter),
                    partial(mdp.add_glossary_term_tooltips, mdp.GLOSSARY_TERM_TOOLTIP_TEMPLATE),
                    mdp.jekyll_front_matter,
                    partial(mdp.write, target),
                ])
                processor.process()

    def _default_template(self, template):
        """Substitute variables and translations."""
        # TODO: initialize translation memory

        with codecs.open(template.source, 'r', 'utf-8') as source:
            with codecs.open(template.destination, 'w+', 'utf-8') as target:
                processor = mdp.MarkdownProcessor(source, filters=[
                    partial(mdp.template, self.cfg.variables),
                    partial(mdp.write, target),
                ])
                processor.process()

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
