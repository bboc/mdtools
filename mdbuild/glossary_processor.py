# -*- coding: utf-8 -*-
from . import markdown_processor as mdp

from . import glossary

# TODO: move this code to glossary module

def get_glossary_processor(style):
    # TODO: this should distinguish between format and style
    if style == 'footnotes':
        return GlossaryFootnoteProcessor()
    elif style == 'underline':
        return GlossaryUnderlineProcessor()
    elif style == 'plain':
        return GlossaryPlainProcessor()
    else:
        return GlossaryMagicProcessor(style)


class GlossaryProcessor(object):
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
        description = glossary.glossary['terms'][term]['glossary']
        return {
            'title': match.group('title'),  # the title of the reference
            'term': term,  # the glossary term (identifier or key in the yaml glossary)
            'name': glossary.glossary['terms'][term]['name'],  # the name of the glossary term
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


class GlossaryMagicProcessor(GlossaryProcessor):
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


class GlossaryPlainProcessor(GlossaryProcessor):
    """Remove all glossary links (replace with link title)."""
    INLINE_TEMPLATE = """%(title)s"""


class GlossaryUnderlineProcessor(GlossaryProcessor):
    """Underline all glossary links."""
    INLINE_TEMPLATE = """`\\underline{%(title)s}`{=latex}"""


class GlossaryFootnoteProcessor(GlossaryProcessor):

    INLINE_TEMPLATE = """%(title)s[^%(term)s]"""
    FOOTNOTE_TEXT_TEMPLATE = """[^%(term)s]: %(name)s: %(description)s"""

    def __init__(self, glossary):
        super(GlossaryFootnoteProcessor, self).__init__(glossary)
        self.buffer = {}

    def additional_item_processing(self, item_data):
        # buffer the explanation
        self.buffer[item_data['term']] = self.FOOTNOTE_TEXT_TEMPLATE % item_data

    def glossary_post_processing(self, target):
        """Emit all the buffered glossary items for footnotes."""
        for key in sorted(self.buffer.keys()):
            target.write(self.buffer[key])
            target.write('\n\n')
