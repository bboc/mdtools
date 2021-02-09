#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

import codecs
from functools import partial
import logging
import shutil
import sys

from . import config
from . import glossary
from . import macros
from .renderer import Renderer, filters

logger = logging.getLogger(__name__)


def process_templates_in_config():
    """Process all templated defined in config.templates."""
    try:
        config.cfg.templates
    except AttributeError:
        logger.warning("no templates defined for preset")
        return

    for t in config.cfg.templates:
        try:
            mode = t.mode
        except AttributeError:
            mode = 'default'
        try:
            source = t.source
        except AttributeError:
            logger.error("source not set for template")
            sys.exit(1)
        try:
            destination = t.destination
        except AttributeError:
            logger.error("no destination for template '%s'" % t.source)
            sys.exit(1)
        template(mode, source, destination)


def template(mode, source, destination):
    """
    Template processing has 3 modes:
    - default: substitute variables and translations
    - copy: simply copy, don't touch
    - markdown: full markdown processing (inkl. jekyll front matter and macros)
    """
    logger.info("processing template: mode='%s', source='%s', destination='%s'" % (mode, source, destination))
    if mode == 'copy':
        shutil.copy(source, destination)
    elif mode in ['html', 'markdown']:
        _processed_template(mode, source, destination)
    elif mode == 'default':
        _default_template(source, destination)
    else:
        logger.error("unknown mode '%s' for template '%s'" % (mode, source))
        sys.exit(1)


def _processed_template(mode, src, dest):
    """
    Run the template through several filters, skip jekyll front matter for
    html templates.
    """

    with codecs.open(src, 'r', 'utf-8') as source:
        with codecs.open(dest, 'w+', 'utf-8') as target:
            renderer = Renderer(source, filters=[
                filters.SkipOnlyFilter.filter,
                filters.inject_variables_and_translations,
                partial(filters.convert_section_links, 'html'),
                partial(macros.MacroFilter.filter),
                filters.unescape_macros,
                # TODO: this is not always the right thing, but glossary entries in templates are pretty rare
                glossary.get_glossary_link_processor('tooltip'),
            ])
            if mode == 'markdown':
                renderer.add_filter(filters.jekyll_front_matter)
            renderer.add_filter(partial(filters.write, target))
            renderer.render()


def _default_template(src, dest):
    """Substitute variables and translations."""

    with codecs.open(src, 'r', 'utf-8') as source:
        with codecs.open(dest, 'w+', 'utf-8') as target:
            renderer = Renderer(source, filters=[
                filters.inject_variables_and_translations,
                partial(filters.write, target),
            ])
            renderer.render()
