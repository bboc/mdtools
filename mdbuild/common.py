# -*- coding: utf-8 -*-

from __future__ import print_function

from contextlib import contextmanager
import markdown
import os
import sys
import yaml


SLIDE_MARKERS = ['---', '***', '* * *']
FILENAME_PATTERN = '%s.md'


def read_config_file(filename):
    stream = open(filename, "r")
    with disable_exception_traceback():
        return yaml.load(stream, Loader=yaml.FullLoader)


def make_pathname(name):
    return name.lower().replace(" ", '-')


def md_filename(name):
    return FILENAME_PATTERN % make_pathname(name)


def create_directory(directory):
    if not os.path.exists(directory):
        os.mkdir(directory)


def increase_headline_level(line):
    line = '#' + line
    if line.endswith('#'):
        line = line + '#'
    return line


@contextmanager
def disable_exception_traceback():
    """
    All traceback information is suppressed and only the exception type
    and value are printed.

    Usage:

    with disable_exception_traceback():
        raise Exception()
    """
    default_value = getattr(sys, "tracebacklimit", 1000)  # `1000` is a Python's default value
    sys.tracebacklimit = 0
    yield
    sys.tracebacklimit = default_value  # revert changes


def make_headline_prefix(config, chapter_idx, section_idx):
    template = config.get('section-prefix', None)
    if template:
        return template % dict(chapter=chapter_idx, section=section_idx)
    else:
        return None


def markdown2html(text):
    return markdown.markdown(text, extensions=['markdown.extensions.extra', 'markdown.extensions.meta'])


class LineWriter(object):

    def __init__(self, target, newlines):
        self.target = target
        if not newlines:
            self.newlines = '\n'
        else:
            self.newlines = newlines
        self.prev_line_empty = False

    def write(self, line):
        """Write line to target, reset blank line counter, output newline if necessary."""
        if self.prev_line_empty:
            self.target.write(self.newlines)
        self.target.write(line.rstrip())
        self.target.write(self.newlines)
        self.prev_line_empty = False

    def mark_empty_line(self):
        self.prev_line_empty = True


HTML_DELIMITERS = {
    "&": "&amp;",
    "'": "&apos;",
    ">": "&gt;",
    "<": "&lt;",
    '"': "&quot;",
}


def escape_html_delimiters(text):
    """Replace html delimiters in text."""
    return "".join(HTML_DELIMITERS.get(c, c) for c in text)
