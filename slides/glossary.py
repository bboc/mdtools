# -*- coding: utf-8 -*-

from common import read_config


GLOSSARY_MARKER = '{{glossary:full}}'


def read_glossary(filename):
    """Read glossary from file if name is given, otherwise return None."""
    if filename:
        return read_config(filename)
    else:
        return None


class GlossaryRenderer(object):
    """Base class for rendering a glossary. Subclasses mostly define class variables."""

    def __init__(self, glossary_path, items_per_page):
        self.glossary = read_glossary(glossary_path)
        self.items_per_page = items_per_page

    def iterate_elements(self):
        self.emit_header()
        for idx, item in enumerate(sorted(self.glossary['terms'].values(), key=lambda value: value['name'])):
            if not (idx + 1) % self.items_per_page:
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

        if continued:
            self.emitter(self.PAGE_BREAK)
            cont = self.glossary['continued']
        else:
            cont = ''
        self.emitter(self.HEADER_TEMPLATE % (self.glossary['title'], cont))


class DecksetGlossaryRenderer(GlossaryRenderer):

    TEMPLATE = "**%(name)s**: %(glossary)s\n"
    HEADER_TEMPLATE = '\n# %s %s\n\n\n'
    PAGE_BREAK = '\n\n---\n\n'


class WordpressGlossaryRenderer(GlossaryRenderer):

    TEMPLATE = "**%(name)s**: %(glossary)s\n"
    HEADER_TEMPLATE = '\n# %s %s\n\n\n'
    PAGE_BREAK = '\n\n---\n\n'

    def __init__(self, glossary_path):
        # no section breaks needed in glossary items!
        # a glossary with more than 9999 items is an abomination
        super(WordpressGlossaryRenderer, self).__init__(glossary_path, 9999)


class HtmlGlossaryRenderer(GlossaryRenderer):

    TEMPLATE = "**%(name)s**: %(glossary)s "
    HEADER_TEMPLATE = '\n# %s %s\n\n\n'
    PAGE_BREAK = '\n\n</section><section>\n'
