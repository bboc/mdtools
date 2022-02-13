# -*- coding: utf-8 -*-

from __future__ import absolute_import

import html
import logging
from operator import itemgetter
import re

from .common import read_config_file, markdown2html
from . import config

logger = logging.getLogger(__name__)

# The actual glossary
glossary = {}


def set_glossary(filename):
    """Read glossary from file if name is given, otherwise return None."""
    if filename:
        g = read_config_file(filename)
        # add the glossary entrie's id to its dictionary (for use in templates)
        for term in g['terms']:
            g['terms'][term]['id'] = term
        globals()['glossary'] = g


def full_glossary_macro(renderer, config, structure):
    """
    Insert full glossary in alphabetical order.
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
        logger.error("can't find '%s' for glossary entry '%s'" % (key, term))
        raise


class GlossaryRenderer(object):
    """
    Base class for rendering a full glossary. If items_per_page is set,
    the glossary spans multiple pages (useful for slide decks).

    Subclasses mostly define:

    cls.ENTRY_TEMPLATE: a template for each entry
    cls.HEADER_TEMPLATE: template for the page header (default: None).
    cls.LIST_PREFIX and cls.LIST_SUFFIX: wrap the list of entries (per page)
       in tags (e.g. <dl>…</dl>) (default: None)
    cls.PAGE_BREAK: page breaks (for multi-page glossaries, e.g. in slide decks),
        page breaks are only emitted when a header template is set.

    """
    HEADER_TEMPLATE = None  # default: no header
    PAGE_BREAK = ''  # requires HEADER_TEMPLATE
    LIST_PREFIX = None  # emitted before the list of entries
    LIST_SUFFIX = None  # emitted after the list of entries

    def __init__(self, items_per_page=None):
        if not glossary:
            raise Exception('glossary not defined')
        self.glossary = glossary

        self.items_per_page = items_per_page

    def iterate_elements(self):
        self.emit_header()
        if self.LIST_PREFIX:
            self.emitter(self.LIST_PREFIX)
        for idx, item in enumerate(sorted(self.glossary['terms'].values(), key=itemgetter('name'))):
            if self.items_per_page and not (idx + 1) % self.items_per_page:
                self.emit_header(True)
            self.emit_entry(item)
        if self.LIST_SUFFIX:
            self.emitter(self.LIST_SUFFIX)

    def render(self, emitter):
        if not self.glossary:
            raise Exception("please specify a glossary!")
        self.emitter = emitter
        self.iterate_elements()

    def emit_entry(self, item):
        self.emitter(self.ENTRY_TEMPLATE % self.format_item(item))

    def format_item(self, item):
        return item

    def emit_header(self, continued=False):

        if self.HEADER_TEMPLATE:
            if continued:
                self.emitter(self.PAGE_BREAK)
                cont = self.glossary['continued']
            else:
                cont = ''
            self.emitter(self.HEADER_TEMPLATE % (self.glossary['title'], cont))


class DecksetGlossaryRenderer(GlossaryRenderer):

    ENTRY_TEMPLATE = "**%(name)s:** %(glossary)s\n\n"
    HEADER_TEMPLATE = '# %s %s\n\n'
    PAGE_BREAK = '\n\n---\n\n'


class RevealjsGlossaryRenderer(GlossaryRenderer):
    # TODO: this produces weird markup in reveal.js, see tests
    ENTRY_TEMPLATE = "**%(name)s:** %(glossary)s"
    HEADER_TEMPLATE = '\n# %s %s\n\n\n'
    PAGE_BREAK = '\n\n</section><section>\n'


class JekyllGlossaryRenderer(GlossaryRenderer):
    """Render glossary as <dd> within a <dl>."""
    # HEADER_TEMPLATE = '---\ntitle: %s %s\n---\n\n'
    LIST_PREFIX = '<dl class="glossary">\n\n'
    ENTRY_TEMPLATE = '<dt id="entry-%(id)s">%(name)s</dt>\n<dd>%(glossary)s</dd>\n\n'
    LIST_SUFFIX = '</dl>\n\n'

    def format_item(self, item):
        html = markdown2html(item['glossary'])
        if html.startswith('<p>'):
            html = html[3:-4]
        item['glossary'] = html
        return item


class MarkdownGlossaryRenderer(GlossaryRenderer):

    ENTRY_TEMPLATE = "**%(name)s:** %(glossary)s\n\n"
    # HEADER_TEMPLATE = '\n# %s %s\n\n'


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


class GlossaryLinkRenderer(object):
    """
    Filter for the renderer that finds and renders glossary links.

    Each subclass renders on specific target format
    """
    GLOSSARY_LINK_PATTERN = re.compile(r'\[(?P<title>[^\]]*)\]\(glossary:(?P<glossary_term>[^)]*)\)')

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
        return data

    @classmethod
    def replace_callback(cls, match):
        """Replace each match of the regex."""
        data = cls.get_item_data(match)
        # do some additional stuff beyond replacing the glossary link inline:
        data = cls.additional_item_processing(data)
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


class GlossaryLinkMagic(GlossaryLinkRenderer):
    """
    Use the config parameter glossary_link_template
    as a template for replacing glossary links.

    Template is set by get_glossary_link_processor at runtime.
    """
    INLINE_TEMPLATE = ''


class GlossaryLinkPlain(GlossaryLinkRenderer):
    """Remove all glossary links (replace with link title)."""
    INLINE_TEMPLATE = """%(title)s"""


class GlossaryLinkTooltip(GlossaryLinkRenderer):
    # INLINE_TEMPLATE = """<dfn data-info="%(name)s: %(description)s">%(title)s</dfn>"""
    # INLINE_TEMPLATE = """<a href="#" class="tooltip" title="%(name)s: %(description)s">%(title)s</a>"""
    INLINE_TEMPLATE = """<a href="glossary.html#entry-%(term)s" class="glossary-tooltip" data-toggle="tooltip" title="%(name)s: %(description)s">%(title)s</a>"""

    @classmethod
    def additional_item_processing(cls, item_data):
        # buffer the explanation
        item_data['description'] = html.escape(item_data['description'])
        return item_data


class GlossaryLinkUnderline(GlossaryLinkRenderer):
    """Underline all glossary links."""
    INLINE_TEMPLATE = """`\\underline{%(title)s}`{=latex}"""


class GlossaryLinkFootnote(GlossaryLinkRenderer):

    INLINE_TEMPLATE = """%(title)s[^%(term)s]"""
    FOOTNOTE_TEXT_TEMPLATE = """[^%(term)s]: %(name)s: %(description)s"""
    buffer = {}

    @classmethod
    def additional_item_processing(cls, item_data):
        # buffer the explanation
        cls.buffer[item_data['term']] = cls.FOOTNOTE_TEXT_TEMPLATE % item_data
        return item_data

    @classmethod
    def glossary_post_processing(cls, target):
        """Emit all the buffered glossary items for footnotes."""
        for key in sorted(cls.buffer.keys()):
            target.write(cls.buffer[key])
            target.write('\n\n')
