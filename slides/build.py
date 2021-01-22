#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Build a slide deck (either in Deckset format or as reveal.js.
"""

from __future__ import unicode_literals

import sys

from config import get_project_config
from structure import get_structure
from glossary import set_glossary
import translate

from build_jekyll import JekyllWriter
from ebook_builder import EbookWriter

TMP_FOLDER = 'tmp-groups'

# TODO: this needs to go somewhere else
translate.read_translation_memory('content/localization.po')


def build(args):
    """Build from the selected configuration."""

    print("setting things up…")
    # read config
    cfg = get_project_config(args.project, args.preset)
    # build glossary (if defined)
    if cfg.glossary:
        set_glossary(cfg.glossary)
    # read structure
    structure = get_structure(cfg.structure, cfg.source)

    # select and run the appropriate builder
    if cfg.renderer == 'revealjs':
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
    elif cfg.renderer == 'jekyll':
        j = JekyllWriter(cfg, structure)
        j.build()
    elif cfg.renderer == 'ebook':
        print("ebook writer not ported to 2.0")
        sys.exit(1)
        e = EbookWriter(cfg)
        e.build()
    else:
        print("unknown renderer", cfg.format)
        sys.exit(1)
