#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Expand macros of the following format

    {{macro}}
    {{macro:param1,param2}}

    {{macro:skip=foo|bar}} returns empty string in presets foo and bar
    {{macro:only=foo|bar}} macro is rendered only in presets foo and bar

Possible enhancements:

- Currently, parameters are only literals, but maybe in the future they can be
  config variables, in a format like {{macro:$name}} or {{macro:var(name)}}
- what about <!-- macros --> are these relevant?
- should a macr be output-aware, with different output per document format,
  or is it enough to simply register different macros for for different formats?

"""
from __future__ import print_function

from functools import partial
import logging
import re

from mdbuild import config
from mdbuild import structure

logger = logging.getLogger(__name__)

macros = {}


def register_macro(name, function):
    """
    Register a macro for processing.
    """
    if name in macros:
        logger.warning("overriding macro '%s'" % name)
    globals()['macros'][name] = function


def process_macro(match, ignore_unknown=False):
    """
    Extract macro name and parameters, call the registered
    macro handler and return the result.
    TODO: handle vars and other substitutions
    """
    macro_string = match.group()[2:-2]

    kwargs = {}
    args = []

    if ':' in macro_string:
        name, params = macro_string.split(':')
        for item in params.split(','):
            if '=' in item:
                key, value = item.split('=')
                kwargs[key] = value
            else:
                args.append(item)
    else:
        name = macro_string

    # process 'skip' and 'only':
    if 'skip' in kwargs:
        if config.cfg.preset in kwargs['skip'].split('|'):
            logger.debug("skipped macro '%s'" % name)
            return ''
    elif 'only' in kwargs:
        if config.cfg.preset not in kwargs['only'].split('|'):
            logger.debug("macro '%s' available only in other presets:" % name)
            return ''

    if name not in macros:
        if not ignore_unknown:
            logger.warning("unknown macro '%s'" % name)
    else:
        return macros[name](config.cfg, structure.structure, *args, **kwargs)


class MacroFilter(object):
    """A markdown processor for expanding macros."""
    MACRO_PATTERN = re.compile(r'\{\{.*?\}\}')

    @classmethod
    def filter(cls, lines, ignore_unknown=False):
        for line in lines:
            line = cls.MACRO_PATTERN.sub(partial(process_macro, ignore_unknown=ignore_unknown), line)
            yield line


class IgnoreMacro(object):
    """
    Simply delete the macro
    """
    @classmethod
    def render(cls, config, structure, *args, **kwargs):
        """Simply ignore everything and return an empty string."""
        return ''
