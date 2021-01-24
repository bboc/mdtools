#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Compile all files so that they can be rendered to LaTEX and ePub.
"""
from __future__ import print_function
from __future__ import absolute_import

import codecs
from functools import partial
import os

from . import markdown_processor as mdp
from .glossary import EbookGlossaryRenderer, glossary


def get_glossary_processor(style, glossary):
    if style == 'footnotes':
        return GlossaryFootnoteProcessor(glossary)
    elif style == 'underline':
        return GlossaryUnderlineProcessor(glossary)
    elif style == 'plain':
        return GlossaryPlainProcessor(glossary)
    else:
        return GlossaryMagicProcessor(glossary, style)


class GlossaryProcessor(object):
    def __init__(self, glossary):
        self.glossary = glossary

    def get_item_data(self, match):
        """Return a dictionary with all data about the glossary item."""
        term = match.group('glossary_term')
        description = self.glossary['terms'][term]['glossary']
        return {
            'title': match.group('title'),  # the title of the reference
            'term': term,  # the glossary term (identifier or key in the yaml glossary)
            'name': self.glossary['terms'][term]['name'],  # the name of the glossary term
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
    """
    def __init__(self, glossary, template):
        super(GlossaryMagicProcessor, self).__init__(glossary)
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


class EbookWriter(object):
    GROUP_INDEX_IMAGE = '\n![inline,fit](img/grouped-patterns/group-%s.png)\n\n'

    def __init__(self, args):
        self.args = args
        self.source_folder = args.source
        self.target_folder = args.target
        self.config = get_config(self.args.config)
        self.glossary_renderer = EbookGlossaryRenderer(self.args.glossary, 9999)
        self.glossary = glossary
        self.gp = get_glossary_processor(args.glossary_style, self.glossary)

    def build(self):
        """Build three files: intro/patterns/appendix."""
        content = self.config[CONTENT]
        # build introduction

        def build_intro_and_appendix(filename, part):
            target_path = os.path.join(self.target_folder, filename)
            with codecs.open(target_path, 'w+', 'utf-8') as target:
                for item in part.sections:
                    self._append_section(target, part, item)

        build_intro_and_appendix('tmp-introduction.md', content.introduction)

        # build all the chapters/sections
        target_path = os.path.join(self.target_folder, 'tmp-chapters.md')
        with codecs.open(target_path, 'w+', 'utf-8') as target:
            for chapter in content.chapters:
                self._build_chapter_index(target, chapter)
                for section in chapter.sections:
                    self._append_section(target,
                                         chapter,
                                         section,
                                         headline_level_increase=1,
                                         headline_prefix=make_headline_prefix(self.args, self.config, chapter.id, section.id))

        # finally build appendix
        build_intro_and_appendix('tmp-appendix.md', content.appendix)

        # emit glossary stuff into tmp-appendix.md if necessary
        with codecs.open(os.path.join(self.target_folder, 'tmp-appendix.md'), 'a', 'utf-8') as target:
            self.gp.glossary_post_processing(target)

    def common_filters(self):
        """Return the set of filters common to all pipelines."""

        return [
            mdp.remove_breaks_and_conts,
            partial(mdp.convert_section_links, mdp.SECTION_LINK_TITLE_ONLY),
            partial(mdp.inject_glossary, self.glossary),

            self.gp.replace_glossary_references,
            partial(mdp.process_summary, mode=mdp.STRIP_MODE),
            mdp.clean_images,
        ]

    def _append_section(self, target, chapter, section, headline_level_increase=0, headline_prefix=None):
        """Append each section to self.target."""
        source_path = os.path.join(self.source_folder, chapter.slug, section.md_filename())
        with codecs.open(source_path, 'r', 'utf-8') as source:
            processor = mdp.MarkdownProcessor(source, filters=self.common_filters())
            processor.add_filter(partial(mdp.prefix_headline, headline_prefix))
            processor.add_filter(partial(mdp.increase_all_headline_levels, headline_level_increase))
            processor.add_filter(partial(mdp.insert_glossary, self.glossary_renderer))
            processor.add_filter(partial(mdp.write, target))
            processor.process()
        target.write("\n\n")

    def _build_chapter_index(self, target, chapter):
        """Add chapter headline, and index.md if present."""

        target.write('\n')
        target.write('## %s \n' % chapter.title)
        target.write('\n')
        # this image is not rendered directly under the headline, so it makes no sense to have this
        # target.write('\n![](img/pattern-groups/group-%s.png)\n\n' % chapter.id)
        chapter_index_file = os.path.join(self.source_folder, chapter.slug, 'index.md')
        if os.path.exists(chapter_index_file):
            with codecs.open(chapter_index_file, 'r', 'utf-8') as cif:
                next(cif)  # skip headline
                processor = mdp.MarkdownProcessor(cif, filters=self.common_filters())
                processor.add_filter(partial(mdp.write, target))
                processor.process()
            target.write('\n\n')
