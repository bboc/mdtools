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

from mdbuild import config
import re

macros = {}


def register_macro(name, function):
    """
    Register a macro for processing.
    """
    if name in macros:
        print('overriding macro:', name)
    globals()['macros'][name] = function


def process_macro(match):
    """
    Extract macro name and parameters, call the registered
    macro handler and return the result.
    TODO: handle vars and other substitutions
    """
    macro_string = match.group()[2:-2]

    kwargs = {}
    args = []
    globals

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
            print('skipped macro:', name)
            return ''
    elif 'only' in kwargs:
        if config.cfg.preset not in kwargs['only'].split('|'):
            print('macro available only in other presets:', name)
            return ''

    # print('macro', name)
    if name not in macros:
        print('warning: unknown macro:', name)
    else:
        return macros[name](*args, **kwargs)


class MacroFilter(object):
    """A markdown processor for expanding macros."""
    MACRO_PATTERN = re.compile("\{\{.*?\}\}")

    @classmethod
    def filter(cls, lines):
        for line in lines:
            line = cls.MACRO_PATTERN.sub(process_macro, line)
            yield line


class IgnoreMacro(object):
    """
    Simply delete the macro
    """
    @classmethod
    def render(cls, *args, **kwargs):
        """Simply ignore everything and return an empty string."""
        return ''
