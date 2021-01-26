# -*- coding: utf-8 -*-

from __future__ import absolute_import
from .common import read_config_file
from operator import itemgetter

GLOSSARY_MARKER = '{{insert-full-glossary}}'

# The actual glossary
glossary = {}


def set_glossary(filename):
    """Read glossary from file if name is given, otherwise return None."""
    if filename:
        globals()['glossary'] = read_config_file(filename)


def glossary_macro(renderer, config, structure):
    """
    Insert full glossary in alphabetical order .
    """

    glossary_contents = []

    def callback(text):
        glossary_contents.append(text)

    renderer.render(callback)
    callback('\n')
    return '\n'.join(glossary_contents)


class GlossaryRenderer(object):
    """Base class for rendering a full glossary. Subclasses mostly define class variables."""

    def __init__(self, items_per_page=None):
        if not glossary:
            raise Exception('glossary not defined')
        self.glossary = glossary

        self.items_per_page = items_per_page

    def iterate_elements(self):
        self.emit_header()
        for idx, item in enumerate(sorted(self.glossary['terms'].values(), key=itemgetter('name'))):
            if self.items_per_page and not (idx + 1) % self.items_per_page:
                self.emit_header(True)
            self.emit_entry(item)

    def render(self, emitter):
        if not self.glossary:
            raise Exception("please specify a glossary!")
        self.emitter = emitter
        self.iterate_elements()

    def emit_entry(self, item):
        self.emitter(self.TEMPLATE % item)

    def emit_header(self, continued=False):

        if self.HEADER_TEMPLATE:
            if continued:
                self.emitter(self.PAGE_BREAK)
                cont = self.glossary['continued']
            else:
                cont = ''
            self.emitter(self.HEADER_TEMPLATE % (self.glossary['title'], cont))


class DecksetGlossaryRenderer(GlossaryRenderer):

    TEMPLATE = "**%(name)s:** %(glossary)s"
    HEADER_TEMPLATE = '# %s %s\n\n'
    PAGE_BREAK = '\n\n---\n\n'


class WordpressGlossaryRenderer(GlossaryRenderer):

    TEMPLATE = "**%(name)s:** %(glossary)s\n"
    HEADER_TEMPLATE = '\n# %s %s\n\n\n'
    PAGE_BREAK = '\n\n---\n\n'

    def __init__(self, glossary_path):
        # no section breaks needed in glossary items!
        # a glossary with more than 9999 items is an abomination
        super(WordpressGlossaryRenderer, self).__init__(glossary_path, 9999)


class HtmlGlossaryRenderer(GlossaryRenderer):
    # TODO: this produces weird markup in reveal.js, see tests
    TEMPLATE = "**%(name)s:** %(glossary)s"
    HEADER_TEMPLATE = '\n# %s %s\n\n\n'
    PAGE_BREAK = '\n\n</section><section>\n'


class JekyllGlossaryRenderer(GlossaryRenderer):

    TEMPLATE = "**%(name)s:** %(glossary)s\n\n"
    # HEADER_TEMPLATE = '---\ntitle: %s %s\n---\n\n'
    HEADER_TEMPLATE = None
    PAGE_BREAK = ''


class EbookGlossaryRenderer(GlossaryRenderer):

    TEMPLATE = "**%(name)s:** %(glossary)s\n\n"
    HEADER_TEMPLATE = '\n## %s %s\n\n'
    #HEADER_TEMPLATE = None
    PAGE_BREAK = ''
