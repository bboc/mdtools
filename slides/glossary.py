# -*- coding: utf-8 -*-

from common import read_config


DECKSET_TEMPLATE = "**%(name)s**: %(glossary)s\n"
HTML_TEMPLATE = "%(name)s\n: %(glossary)s"
GLOSSARY_MARKER = '{{glossary:full}}'


def read_glossary(filename):
    """Read glossary from file if name is given, otherwise return None."""
    if filename:
        return read_config(filename)
    else:
        return None


class GlossaryRenderer(object):

    def __init__(self, glossary, emitter):
        self.glossary = glossary
        self.emitter = emitter

    def iterate_elements(self):
        self.emit_header()
        for idx, item in enumerate(sorted(self.glossary['terms'].values(), key=lambda value: value['name'])):
            if not (idx + 1) % self.ITEMS_PER_PAGE:
                self.emit_header(True)
            self.emit_entry(item)

    def render(self):
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
    HEADER_TEMPLATE = '\n# %s %s\n\n'
    PAGE_BREAK = '\n\n---\n\n'
    ITEMS_PER_PAGE = 19
