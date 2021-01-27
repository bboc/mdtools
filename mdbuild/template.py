#!/usr/bin/env python
# -*- coding: utf-8 -*-


from __future__ import absolute_import
import codecs
from functools import partial

import sys
import shutil
from . import config
from . import markdown_processor as mdp
from . import macros


def process_templates_in_config():
    """Process all templated defined in config.templates."""
    try:
        config.cfg.templates
    except AttributeError:
        print("WARNING: no templates defined for preset")
        return

    for t in config.cfg.templates:
        try:
            mode = t.mode
        except AttributeError:
            mode = 'default'
        try:
            source = t.source
        except AttributeError:
            print('ERROR: template has no source')
            sys.exit(1)
        try:
            destination = t.destination
        except AttributeError:
            print('ERROR: no destination for template', t.source)
            sys.exit(1)
        template(mode, source, destination)


def template(mode, source, destination):
    """
    Template processing has 3 modes:
    - default: substitute variables and translations
    - copy: simply copy, don't touch
    - markdown: full markdown processing (inkl. jekyll front matter and macros)
    """
    print(mode, source, destination)
    if mode == 'copy':
        shutil.copy(source, destination)
    elif mode in ['html', 'markdown']:
        _processed_template(mode, source, destination)
    elif mode == 'default':
        _default_template(source, destination)
    else:
        print("ERROR: unknown mode ", mode, 'for template', source)
        sys.exit(1)


def _processed_template(mode, src, dest):
    """
    Run the template through several filters, skip jekyll front matter for
    html templates.
    """

    with codecs.open(src, 'r', 'utf-8') as source:
        with codecs.open(dest, 'w+', 'utf-8') as target:
            processor = mdp.MarkdownProcessor(source, filters=[

                partial(mdp.template, config.cfg.variables),
                partial(mdp.convert_section_links, mdp.SECTION_LINK_TO_HMTL),
                partial(macros.MacroFilter.filter),
                # TODO: this is not always the right thing, but glossary entries in templates are pretty rare
                partial(mdp.add_glossary_term_tooltips, mdp.GLOSSARY_TERM_TOOLTIP_TEMPLATE)])
            if mode == 'markdown':
                processor.add_filter(mdp.jekyll_front_matter)
            processor.add_filter(partial(mdp.write, target))
            processor.process()


def _default_template(src, dest):
    """Substitute variables and translations."""

    with codecs.open(src, 'r', 'utf-8') as source:
        with codecs.open(dest, 'w+', 'utf-8') as target:
            processor = mdp.MarkdownProcessor(source, filters=[
                partial(mdp.template, config.cfg.variables),
                partial(mdp.write, target),
            ])
            processor.process()
