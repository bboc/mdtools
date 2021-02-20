#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

import re
from string import Template

from .common import markdown2html, SLIDE_MARKERS


class Slide(object):

    IMG_TEMPLATE = '![](%s)'
    IMG_PATTERN = re.compile(r"\!\[(?P<format>.*)\]\((?P<url>.*)\)")
    HEADLINE_PATTERN = re.compile(r"^(?P<level>#+)(?: ?(?:\[fit\])? ?)(?P<text>.*)$")
    HEADLINE = Template("$level $text\n")
    FLOATING_IMAGE = Template(
        """<div class="float-right"><img src="$url" /></div>\n\n""")

    class EndOfFile(Exception):
        pass

    def __init__(self, glossary_renderer):
        self.glossary_renderer = glossary_renderer
        self.headline = None
        self.background_img = None
        self.content = []
        self.speaker_notes = []
        self.floating_image = None
        self.is_empty = True

    def read(self, source):
        """Read source until end of slide or end of file."""

        def emitter(line):
            self.content.append(line)
        for line in source:
            self.is_empty = False
            L = line.strip()
            if L in SLIDE_MARKERS:
                return  # slide end
            elif L == GLOSSARY_MARKER:
                    self.glossary_renderer.render(emitter)
            elif L.startswith('#'):
                headline = self.process_headline(L)
                if not self.headline:
                    self.headline = headline
                else:
                    self.content.append(headline)
            elif L.startswith("![") and L.endswith(')'):
                # process image
                self.process_image(L)
            elif L.startswith('^'):
                self.speaker_notes.append(line[1:])
            else:
                self.content.append(line)
        else:
            raise self.EndOfFile()

    def process_image(self, line):
        """Identify background and floating images, add all others to content.."""
        # TODO: convert background images (needs two pass and buffer)
        m = self.IMG_PATTERN.match(line)
        format, image_url = (m.group('format').lower(), m.group('url'))
        if 'right' in format:
            self.floating_image = image_url
        elif format == 'fit':
            self.background_img = image_url
        else:
            self.content.append('![](%s)' % image_url)

    def process_headline(self, headline):
        """Remove [fit] from headline."""
        m = self.HEADLINE_PATTERN.match(headline)
        return self.HEADLINE.substitute(level=m.group('level'), text=m.group('text'))

    def slide_start(self, target):
        if self.background_img:
            target.write("""<section data-background-image="%s">\n""" % self.background_img)
        else:
            target.write("<section>\n")

    def slide_end(self, target):
        target.write("</section>\n\n")

    def render(self, target):
        if self.is_empty:
            return

        self.slide_start(target)
        if self.headline:
            target.write(markdown2html(self.headline))
            target.write("\n")

        if self.floating_image:
            target.write("""<div class="float-left">\n""")
            target.write(markdown2html("".join(self.content)))
            target.write('</div>\n')
            target.write(self.FLOATING_IMAGE.substitute(url=self.floating_image))

        else:
            target.write(markdown2html("".join(self.content)))
            target.write("\n")

        if self.speaker_notes:
            target.write("""<aside class="notes">\n""")
            target.write(markdown2html("".join(self.speaker_notes)))
            target.write('</aside>')

        self.slide_end(target)
