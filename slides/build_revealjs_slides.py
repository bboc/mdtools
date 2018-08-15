#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Build the All Patterns Explained slide deck in reveal.js format.
"""

import codecs
import os

from common import make_pathname, get_config
from common import TITLE, FRONT_MATTER, CHAPTERS, APPENDIX, END, SKIP, CONTENT, SLUG

from glossary import HtmlGlossaryRenderer
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
    """Convert title, front-matter, chapters, appendix and end to HTML and write to target."""

    def __init__(self, config, source, glossary_path, glossary_items):
        self.config = get_config(config)
        self.source_folder = source
        self.glossary_renderer = HtmlGlossaryRenderer(glossary_path, glossary_items)

    def write(self, target):
        """Called from RevealJsWriter."""

        content = self.config[CONTENT]
        self.target = target
        self._append_section(content[TITLE])
        if FRONT_MATTER in content:
            self._append_section(content[FRONT_MATTER][SLUG])
        for chapter in content[CHAPTERS]:
            self._append_section(chapter[SLUG])
        if APPENDIX in content:
            self._append_section(content[APPENDIX][SLUG])
        if content[END] != SKIP:
            self._append_section(content[END])

    def _start_section(self):
        self.target.write('<section>')

    def _end_section(self):
        self.target.write('</section>')

    def _append_section(self, filename):
        filename = '%s.md' % make_pathname(filename)
        self._start_section()
        c = RevealJsHtmlConverter(os.path.join(self.source_folder, filename), self.glossary_renderer)
        c.write(self.target)
        self._end_section()
