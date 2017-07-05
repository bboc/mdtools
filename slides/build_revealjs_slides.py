#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Build the All Patterns Explained slide deck in reveal.js format.
"""

import codecs
import os

from common import make_pathname, read_config
from revealjs_converter import RevealJsHtmlConverter


class RevealJsWriter(object):
    """Inject output of content_writer into a template."""

    CONTENT_MARKER = "<!-- INSERT-CONTENT -->"

    def __init__(self, target_path, template_path, content_writer):
        self.target_path = target_path
        self.template_path = template_path
        self.content_writer = content_writer

    def build(self):
        with codecs.open(self.target_path, 'w+', 'utf-8') as self.target:
            with codecs.open(self.template_path, 'r', 'utf-8') as self.template:

                self.copy_template_header()
                self.content_writer.write(self.target)
                self.copy_template_footer()

    def copy_template_header(self):
        for line in self.template:
            if line.strip() == self.CONTENT_MARKER:
                break
            else:
                self.target.write(line)

    def copy_template_footer(self):
        for line in self.template:
            self.target.write(line)


class RevealJSBuilder(object):
    """Convert title, intro, chapters, closing and end to HTML and write to target."""

    def __init__(self, config, source):
        self.config = read_config(config)
        self.source_folder = source

    def write(self, target):
        """Called from RevealJsWriter."""

        self.target = target
        # title
        self._append_section('title.md')
        # introduction
        if self.config.has_key('introduction'):
            self._append_section('introduction.md')
        # chapters
        for chapter in self.config['chapter_order']:
            self._append_section( '%s.md' % make_pathname(chapter))
        
        # closing 
        if self.config.has_key('closing'):
            self._append_section('closing.md')
        # end
        self._append_section('end.md')

    def _start_section(self):
        self.target.write('<section>')

    def _end_section(self):
        self.target.write('</section>')

    def _append_section(self, filename):
        self._start_section()
        c = RevealJsHtmlConverter(os.path.join(self.source_folder, filename))
        c.write(self.target)
        self._end_section()


