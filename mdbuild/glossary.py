# -*- coding: utf-8 -*-

from __future__ import absolute_import
from .common import read_config_file
from operator import itemgetter
from . import markdown_processor as mdp

GLOSSARY_MARKER = '{{insert-full-glossary}}'

# The actual glossary
glossary = {}


def set_glossary(filename):
    """Read glossary from file if name is given, otherwise return None."""
    if filename:
        globals()['glossary'] = read_config_file(filename)


def full_glossary_macro(renderer, config, structure):
    """
    Insert full glossary in alphabetical order .
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
    # TODO: this should distinguish between format and style
    if style == 'footnotes':
        return GlossaryLinkFootnoteProcessor()
    elif style == 'underline':
        return GlossaryLinkUnderlineProcessor()
    elif style == 'plain':
        return GlossaryLinkPlainProcessor()
    else:
        return GlossaryLinkMagicProcessor(style)


class GlossaryLinkProcessor(object):
    """
    This is the a glossary processor that replaces glossary links, it works like this:

    gp = get_glossary_processor(style)

    then append this to a markdown processor:

    self.gp.replace_glossary_references

    TODO: The API is a bit lame, the first line should not be necessary
    TODO: teach this pony to replace glossary links
    """

    def __init__(self):
        pass

    def get_item_data(self, match):
        """Return a dictionary with all data about the glossary item."""
        term = match.group('glossary_term')
        description = glossary['terms'][term]['glossary']
        return {
            'title': match.group('title'),  # the title of the reference
            'term': term,  # the glossary term (identifier or key in the yaml glossary)
            'name': glossary['terms'][term]['name'],  # the name of the glossary term
            'description': description,  # the explanation of the term
        }

    def additional_item_processing(self, data):
        """Override for additional processing for each glossary item."""
        pass

    def replace_callback(self, match):
        """Replace each match of the regex."""
        data = self.get_item_data(match)
        # do some additional stuff beyond replacing the glossary link inline:
        self.additional_item_processing(data)
        return self.INLINE_TEMPLATE % data

    def replace_glossary_references(self, lines):
        """Replace all inline glossary reference."""
        for line in lines:
            line = mdp.GLOSSARY_TERM_PATTERN.sub(self.replace_callback, line)
            yield line

    def glossary_post_processing(self, target):
        """Override to do something when after the complete ebook is processed, e.g. insert footnotes."""
        pass


class GlossaryLinkMagicProcessor(GlossaryLinkProcessor):
    """
    Use the argument --glossary-style as a template for replacing glossary links.
    make sure to escape backticks etc. "\`\\underline{%(title)s}\`{=latex}"
    TODO: this is probably best configured in the project.yaml in the future
    """
    def __init__(self, template):
        super(GlossaryMagicProcessor, self).__init__()
        print(template)
        print("--------------------")
        self.INLINE_TEMPLATE = template


class GlossaryLinkPlainProcessor(GlossaryLinkProcessor):
    """Remove all glossary links (replace with link title)."""
    INLINE_TEMPLATE = """%(title)s"""


class GlossaryLinkUnderlineProcessor(GlossaryLinkProcessor):
    """Underline all glossary links."""
    INLINE_TEMPLATE = """`\\underline{%(title)s}`{=latex}"""


class GlossaryLinkFootnoteProcessor(GlossaryLinkProcessor):

    INLINE_TEMPLATE = """%(title)s[^%(term)s]"""
    FOOTNOTE_TEXT_TEMPLATE = """[^%(term)s]: %(name)s: %(description)s"""

    def __init__(self):
        super(GlossaryLinkFootnoteProcessor, self).__init__()
        self.buffer = {}

    def additional_item_processing(self, item_data):
        # buffer the explanation
        self.buffer[item_data['term']] = self.FOOTNOTE_TEXT_TEMPLATE % item_data

    def glossary_post_processing(self, target):
        """Emit all the buffered glossary items for footnotes."""
        for key in sorted(self.buffer.keys()):
            target.write(self.buffer[key])
            target.write('\n\n')


