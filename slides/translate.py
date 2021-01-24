#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
A tiny implementation of gettext-like translation.
"""
from __future__ import print_function

import os.path
import polib

translation_memory = {}


def read_translation_memory(filename):
    """Read translation memory from a po-file."""
    if not os.path.exists(filename):
        print(">>>translation memory not found:", filename, "<<<")
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
            print("WARNING: ", message, "not in translation translation_memory")
        return message
