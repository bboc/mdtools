#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Build the All Patterns Explained slide deck in reveal.js format.
"""
from __future__ import absolute_import

import codecs
import os
import re
from string import Template


from .common import md_filename, LineWriter, increase_headline_level, SLIDE_MARKERS
from . import config
from .slides import Slide


class RevealJsWriter(object):
    """Inject output of a content_writer into a template."""

    CONTENT_MARKER = "<!-- INSERT-CONTENT -->"

    def __init__(self):
        pass

    def build(self, content_writer):
        with codecs.open(config.cfg.target, 'w+', 'utf-8') as self.target:
            with codecs.open(config.cfg.template, 'r', 'utf-8') as self.template:

                self.copy_template_header()
                content_writer.write(self.target)
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


class RevealJSBuilderOld(object):
    """Convert title, front-matter, chapters, appendix and end to HTML and write to target."""

    def __init__(self):
        self.source_folder = source
        self.glossary_renderer = HtmlGlossaryRenderer(glossary_path, glossary_items)

    def write(self, target):
        """Called from RevealJsWriter."""

        content = self.config[CONTENT]
        self.target = target
        self._append_section(md_filename(content.title))
        if content.introduction:
            self._append_section(content.introduction.md_filename())
        for chapter in content.chapters:
            self._append_section(chapter.md_filename())
        if content.appendix:
            self._append_section(content.appendix.md_filename())
        if content.end:
            self._append_section(md_filename(content.end))

    def _start_section(self):
        self.target.write('<section>')

    def _end_section(self):
        self.target.write('</section>')

    def _append_section(self, filename):
        self._start_section()
        c = RevealJsHtmlConverter(os.path.join(self.source_folder, filename), self.glossary_renderer)
        c.write(self.target)
        self._end_section()


class RevealJsHtmlConverter(object):
    """
    Convert one decset file to revealjs. used by revealjs converter and
    revealjs builder!
    """
    def __init__(self, source_path, glossary_renderer):
        self.source_path = source_path
        self.glossary_renderer = glossary_renderer

    def write(self, target):
        # target.write('<section>')
        with codecs.open(self.source_path, 'r', 'utf-8') as source:
            while True:
                slide = Slide(self.glossary_renderer)
                try:
                    slide.read(source)
                except Slide.EndOfFile:
                    break
                finally:
                    slide.render(target)
        # target.write('</section>')


class RevealJSMarkdownConverter(object):
    """
    Convert Deckset Markdown to Reveal.js Markdown slides.

    Untested. Has known issues with image placement and other things.
    Might still be helpful sometime because the new converter can only output HTML.
    """
    SLIDE_START = """
    <section data-markdown>
        <script type="text/template">
    """

    SLIDE_END = """
        </script>
    </section>
    """

    IMG_TEMPLATE = '![](%s)'
    IMG_PATTERN = re.compile(r"\!\[(.*)\]\((.*)\)")
    FLOATING_IMAGE = Template(
        """<img class="float-right" src="$url" width="50%" />""")

    def convert_to_reveal(self, source, target):
        lw = LineWriter(target, source.newlines)
        for line in source:
            L = line.strip()
            if not L:
                lw.mark_empty_line()
            elif L in SLIDE_MARKERS:
                lw.write(self.SLIDE_END)
                lw.write(self.SLIDE_START)
                # omit line, do not change empty line marker!
                pass
            elif L.startswith('##'):
                lw.write(increase_headline_level(L))
            elif line.lstrip().startswith("!["):
                # fix image
                m = self.IMG_PATTERN.match(L)
                lw.write(self.convert_image(m.group(1), m.group(2)))
            else:
                lw.write(line)

    def convert_image(self, format, img_url):
        """Replace floating images with img tag, pass all others."""
        format = format.lower()
        if 'right' in format:
            return self.FLOATING_IMAGE.substitute(url=img_url)
        else:
            return '![](%s)' % img_url

