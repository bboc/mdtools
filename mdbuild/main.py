#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Build a slide deck (either in Deckset format or as reveal.js.
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import

import sys
import argparse

from .build_jekyll import JekyllWriter
from .build_ebook import EbookWriter
from .config import get_project_config
from .structure import get_structure
from .glossary import set_glossary
from . import template
from . import translate


def build(args):
    """Build from the selected configuration."""

    cfg = setup(args)
    # read structure
    structure = get_structure(cfg.structure, cfg.source)

    # select and run the appropriate builder
    if cfg.renderer == 'jekyll':
        j = JekyllWriter(cfg, structure)
        j.build()
    elif cfg.renderer == 'ebook':
        e = EbookWriter(cfg, structure)
        e.build()
    elif cfg.renderer == 'revealjs':
        print("revealjs writer not ported to 2.0")
        sys.exit(1)
        build_reveal_slides(cfg)
    elif cfg.renderer == 'deckset':
        print("Deckset writer not ported to 2.0")
        sys.exit(1)
        build_deckset_slides(cfg)
    elif cfg.renderer == 'wordpress':
        print("Wordpress writer not ported to 2.0")
        sys.exit(1)
        build_wordpress(cfg)
    else:
        print("ERROR: unknown renderer", cfg.format)
        sys.exit(1)


def setup(args):
    print("setting things up…")
    # read config
    cfg = get_project_config(args.project, args.preset)
    # build glossary (if defined)
    if cfg.glossary:
        set_glossary(cfg.glossary)
    else:
        print('WARNING: no glossary defined!')

    translate.read_translation_memory(cfg.localization)
    return cfg


def main_build():
    parser = argparse.ArgumentParser(
        description='A commandline tools for publishing various document formats (Jekyll, LaTeX, ePub etc.) from a single markdown source.',
        fromfile_prefix_chars='@'
    )
    parser.add_argument('--verbose', '-v', action='count')
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
    # TODO: test command
    parser = argparse.ArgumentParser(
        description="Inject translations (and optionally parameters from a config) into a template file.",
        fromfile_prefix_chars='@'
    )
    parser.add_argument('--verbose', '-v', action='count')
    parser.add_argument('mode', choices=['copy', 'markdown', 'default'],
                        default='default',
                        help="Output format (deckset | ebook | jekyll | revealjs | wordpress)")
    parser.add_argument('preset',
                        help="The preset (defined in the project configuration file) to use.")
    parser.add_argument('project', help='the configuration file for the project (yaml)')

    parser.add_argument('source', help='Source template')
    parser.add_argument('target', help='Filename for the resulting template')
    args = parser.parse_args()

    cfg = setup(args)

    template(args.mode, args.source, args.destination, cfg)
