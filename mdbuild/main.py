#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Build a slide deck (either in Deckset format or as reveal.js.
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import

import logging
import sys
import argparse

from .build_deckset_slides import DecksetWriter
from .build_ebook import EbookWriter
from .build_jekyll import JekyllWriter
from .build_revealjs_slides import RevealJsWriter, RevealJSBuilder

from . import config
from .structure import set_structure
from .glossary import set_glossary
from .template import template
from . import translate

logger = logging.getLogger(__name__)


def build(args):
    """Build from the selected configuration."""

    print('------- Starting Build ---------')

    logger.debug("args: %s" % repr(args))

    setup(args)

    # read structure
    set_structure(config.cfg.structure, config.cfg.source)

    logger.info("selecting the renderer...")

    # select and run the appropriate builder
    if config.cfg.renderer == 'jekyll':
        j = JekyllWriter()
        j.build()
    elif config.cfg.renderer == 'ebook':
        e = EbookWriter()
        e.build()
    elif config.cfg.renderer == 'revealjs':
        cw = RevealJSBuilder(args.config, args.source, args.glossary, args.glossary_items)
        rw = RevealJsWriter(args.target, args.template, cw)
        rw.build()
    elif config.cfg.renderer == 'deckset':
        r = DecksetWriter()
        r.build()
    else:
        logger.error("unknown renderer '%s' " % config.cfg.format)
        sys.exit(1)


def setup(args):

    # set up logger first
    logging_setup(args)
    logger.info("setting things up...")

    # read config
    config.set_project_config(args.project, args.preset)
    # build glossary (if defined)
    if config.cfg.glossary:
        set_glossary(config.cfg.glossary)
    else:
        logger.warning('no glossary defined!')

    translate.read_translation_memory(config.cfg.localization)


def logging_setup(args):
    """
    -v show warnings
    -vv show info
    -vvv DEBUG and a formatter that shows the module
    """

    def suppress_markdown_messages(record):
        """Suppress all the noise the markdown module makes."""
        if record.name == 'MARKDOWN':
            return 0
        else:
            return 1

    # calculate format from verbose
    lvl = max(40 - (10 * args.verbose), 10)
    if lvl == logging.DEBUG:
        FORMAT = '%(levelname)s::%(name)s::%(message)s'
    else:
        FORMAT = '%(message)s'
    h = logging.StreamHandler(stream=sys.stdout)
    h.addFilter(suppress_markdown_messages)
    h.setFormatter(logging.Formatter(FORMAT))
    if logging.root.hasHandlers():
        print("has handlers")
    logging.root.addHandler(h)

    logging.root.setLevel(lvl)

    logging.getLogger('mdbuild.macros.core').addHandler(logging.NullHandler())


def main_build():
    parser = argparse.ArgumentParser(
        description='A commandline tools for publishing various document formats (Jekyll, LaTeX, ePub etc.) from a single markdown source.',
        fromfile_prefix_chars='@'
    )
    parser.add_argument('--verbose', '-v', action='count', default=0)
    parser.add_argument('preset',
                        help="The preset (defined in the project configuration file) to use for this build.")
    parser.add_argument('project', help='the configuration file for the project (yaml)')

    args = parser.parse_args()
    build(args)


def main_template():
    """
    Copy a template to destination, potentially
    using config vars and even a strcuture file...

    TODO: this needs some tweaking:
    - it should run with a minimal config file (variables, glossary, structure)
    - it shuld also run with a full configuration (with an existing or a dedicated preset)
    - therefore preset should be optional
    - to make use of project structure, structure needs to be globally accessible.
    """
    parser = argparse.ArgumentParser(
        description="Inject translations (and optionally parameters from a config) into a template file.",
        fromfile_prefix_chars='@'
    )
    parser.add_argument('--verbose', '-v', action='count', default=0)
    parser.add_argument('mode', choices=['copy', 'markdown', 'default'],
                        default='default',
                        help="Output format (deckset | ebook | jekyll | revealjs | wordpress)")
    parser.add_argument('--preset',
                        help="The preset (defined in the project configuration file) to use.")
    parser.add_argument('project', help='the configuration file for the project (yaml)')

    parser.add_argument('source', help='Source template')
    parser.add_argument('target', help='Filename for the resulting template')
    args = parser.parse_args()

    setup(args)

    template(args.mode, args.source, args.target)
