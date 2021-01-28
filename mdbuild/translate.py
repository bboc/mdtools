#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
A tiny implementation of gettext-like translation.
"""
from __future__ import print_function

import logging
import os.path
import polib

logger = logging.getLogger(__name__)

translation_memory = {}


def read_translation_memory(filename):
    """Read translation memory from a po-file."""
    if not os.path.exists(filename):
        logger.warning("translation memory not found: '%s'", filename)
        return
    tm = {}
    po = polib.pofile(filename)
    for entry in po.translated_entries():
        if not entry.obsolete:
            tm[entry.msgid] = entry.msgstr
    globals()["translation_memory"] = tm


def translate(message, warnings=None):
    if message in translation_memory:
        return translation_memory[message]
    else:
        if warnings:
            logger.warning("message not in translation translation_memory: '%s'", message)
        return message
