#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Build the All Patterns Explained slide deck in Deckset format.
"""

import codecs
from functools import partial
import os

from common import make_pathname, get_config
from common import TITLE, FRONT_MATTER, APPENDIX, END, SKIP, SLUG, CHAPTERS
from glossary import DecksetGlossaryRenderer
import markdown_processor as mdp


class DecksetWriter(object):
    CONTENT_MARKER = "<!-- INSERT-CONTENT -->"
    GROUP_INDEX_IMAGE = '\n![inline,fit](img/grouped-patterns/group-%s.png)\n\n'

    def __init__(self, args):
        self.args = args
        self.template_path = self.args.template
        self.source_folder = args.source
        self.config = get_config(self.args.config)
        self.glossary_renderer = DecksetGlossaryRenderer(self.args.glossary, self.args.glossary_items)

    def build(self):
        with codecs.open(self.args.target, 'w+', 'utf-8') as self.target:
            with codecs.open(self.template_path, 'r', 'utf-8') as self.template:
                self._copy_template_header()

                content = self.config['content']
                if content[TITLE] != SKIP:
                    self._append_section(content[TITLE])

                if FRONT_MATTER in content:
                    self._append_section(content[FRONT_MATTER][SLUG])

                # add all the groups
                for chapter in content[CHAPTERS]:
                    self._append_section(chapter[SLUG])

                if APPENDIX in content:
                    self._append_section(content[APPENDIX][SLUG])

                if content[END] != SKIP:
                    self._append_section(content[END], skip_section_break=True)

                self._copy_template_footer()

    def _copy_template_header(self):
        for line in self.template:
            if line.strip() == self.CONTENT_MARKER:
                break
            else:
                self.target.write(line)

    def _copy_template_footer(self):
        for line in self.template:
            self.target.write(line)

    def _append_section(self, name, skip_section_break=False):
        name = '%s.md' % name
        with codecs.open(os.path.join(self.source_folder, name), 'r', 'utf-8') as source:
            processor = mdp.MarkdownProcessor(source, filters=[
                partial(mdp.convert_section_links, mdp.SECTION_LINK_TITLE_ONLY),
                partial(mdp.insert_glossary, self.glossary_renderer),
                partial(mdp.write, self.target),
            ])
            processor.process()

        if not skip_section_break:
            self.target.write('\n\n---\n\n')
