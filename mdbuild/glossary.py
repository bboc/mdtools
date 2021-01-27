# -*- coding: utf-8 -*-

from __future__ import absolute_import
from .common import read_config_file
from . import config
from operator import itemgetter
from .common import escape_html_delimiters
import re

GLOSSARY_MARKER = '{{insert-full-glossary}}'

# The actual glossary
glossary = {}


def set_glossary(filename):
    """Read glossary from file if name is given, otherwise return None."""
    if filename:
        globals()['glossary'] = read_config_file(filename)


def full_glossary_macro(renderer, config, structure):
    """
    Insert full glossary in alphabetical order.

    TODO: this should be format aware....
    """

    glossary_contents = []

    def callback(text):
        glossary_contents.append(text)

    renderer.render(callback)
    callback('\n')
    return '\n'.join(glossary_contents)


def glossary_term_macro(renderer, config, term):
    """Expand glossary term."""
    return _expand_term(term, 'glossary', "%s")


def glossary_definition_macro(renderer, config, term):
    """Expand glossary term definition."""
    return _expand_term(term, 'definition', "_%s_")


def _expand_term(term, key, pattern):
    """Return glossary entry or definition."""
    try:
        return pattern % glossary['terms'][term][key]
    except KeyError:
        print('cant find ', key, " for glossary entry ", term)
        raise


# TODO: unify this with the other glossary code!!
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


def get_glossary_link_processor(style):
    """Return a filter that processes glossary links."""

    if style == 'footnotes':
        return GlossaryLinkFootnote.replace_glossary_references
    elif style == 'underline':
        return GlossaryLinkUnderline.replace_glossary_references
    elif style == 'plain':
        return GlossaryLinkPlain.replace_glossary_references
    elif style == 'tooltip':
        return GlossaryLinkTooltip.replace_glossary_references
    else:
        GlossaryLinkMagic.INLINE_TEMPLATE = config.glossary_template
        return GlossaryLinkMagic.replace_glossary_references


class GlossaryLinkProcessor(object):
    """
    This is the a glossary processor that replaces glossary links.
    """
    GLOSSARY_LINK_PATTERN = re.compile("\[(?P<title>[^\]]*)\]\(glossary:(?P<glossary_term>[^)]*)\)")

    @classmethod
    def get_item_data(cls, match):
        """Return a dictionary with all data about the glossary item."""
        term = match.group('glossary_term')
        description = glossary['terms'][term]['glossary']
        return {
            'title': match.group('title'),  # the title of the reference
            'term': term,  # the glossary term (identifier or key in the yaml glossary)
            'name': glossary['terms'][term]['name'],  # the name of the glossary term
            'description': description,  # the explanation of the term
        }

    @classmethod
    def additional_item_processing(cls, data):
        """Override for additional processing for each glossary item."""
        pass

    @classmethod
    def replace_callback(cls, match):
        """Replace each match of the regex."""
        data = cls.get_item_data(match)
        # do some additional stuff beyond replacing the glossary link inline:
        cls.additional_item_processing(data)
        return cls.INLINE_TEMPLATE % data

    @classmethod
    def replace_glossary_references(cls, lines):
        """Replace all inline glossary reference."""
        for line in lines:
            line = cls.GLOSSARY_LINK_PATTERN.sub(cls.replace_callback, line)
            yield line

    @classmethod
    def glossary_post_processing(cls, target):
        """Override to do something when after the complete ebook is processed, e.g. insert footnotes."""
        pass


class GlossaryLinkMagic(GlossaryLinkProcessor):
    """
    Use the config parameter glossary_link_template
    as a template for replacing glossary links.

    Template is set by get_glossary_link_processor at runtime.
    """
    INLINE_TEMPLATE = ''


class GlossaryLinkPlain(GlossaryLinkProcessor):
    """Remove all glossary links (replace with link title)."""
    INLINE_TEMPLATE = """%(title)s"""


class GlossaryLinkUnderline(GlossaryLinkProcessor):
    """Underline all glossary links."""
    INLINE_TEMPLATE = """`\\underline{%(title)s}`{=latex}"""


class GlossaryLinkFootnote(GlossaryLinkProcessor):

    INLINE_TEMPLATE = """%(title)s[^%(term)s]"""
    FOOTNOTE_TEXT_TEMPLATE = """[^%(term)s]: %(name)s: %(description)s"""
    buffer = {}

    @classmethod
    def additional_item_processing(cls, item_data):
        # buffer the explanation
        cls.buffer[item_data['term']] = cls.FOOTNOTE_TEXT_TEMPLATE % item_data

    @classmethod
    def glossary_post_processing(cls, target):
        """Emit all the buffered glossary items for footnotes."""
        for key in sorted(cls.buffer.keys()):
            target.write(cls.buffer[key])
            target.write('\n\n')


class GlossaryLinkTooltip(GlossaryLinkProcessor):
    INLINE_TEMPLATE = """<dfn data-info="%(name)s: %(description)s">%(title)s</dfn>"""
