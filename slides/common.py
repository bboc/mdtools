#!/usr/bin/env python

import os
import yaml
import markdown

def make_pathname(name):
    return name.lower().replace(" ", '-')


def make_title(name):
    return name.title().replace('s3', 'S3')


def create_directory(directory):
    if not os.path.exists(directory):
        os.mkdir(directory)


def read_config(filename):
	stream = open(filename, "r")
	return yaml.load(stream)


def increase_headline_level(line):
    line = '#' + line
    if line.endswith('#'):
        line = line + '#'
    return line


def markdown2html(text):
    return markdown.markdown(text,['markdown.extensions.extra', 'markdown.extensions.meta'])


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
