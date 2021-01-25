#!/usr/bin/env python
# -*- coding: utf-8 -*-


from __future__ import absolute_import
import codecs
from functools import partial

import sys
import shutil
from . import markdown_processor as mdp
from . import macros


def copy_templates(cfg):
    """
    Copy templates to destination.

    template processing has 3 modes:
    - default: substitute variables and translations
    - copy: simply copy, don't touch
    - markdown: full markdown processing (inkl. jekyll front matter and macros)
    """
    for t in cfg.templates:
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
            _markdown_template(t)
        elif mode == 'default':
            _default_template(t)
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


def _default_template(template, cfg):
    """Substitute variables and translations."""

    with codecs.open(template.source, 'r', 'utf-8') as source:
        with codecs.open(template.destination, 'w+', 'utf-8') as target:
            processor = mdp.MarkdownProcessor(source, filters=[
                partial(mdp.template, cfg.variables),
                partial(mdp.write, target),
            ])
            processor.process()
