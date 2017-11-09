#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Build the All Patterns Explained slide deck in Deckset format.
"""

import codecs

import os

from common import make_pathname, read_config
from glossary import read_glossary, GLOSSARY_MARKER, DecksetGlossaryRenderer


class DecksetWriter(object):
    CONTENT_MARKER = "<!-- INSERT-CONTENT -->"
    GROUP_INDEX_IMAGE = '\n![inline,fit](img/grouped-patterns/group-%s.png)\n\n'

    def __init__(self, args):
        self.args = args
        self.template_path = self.args.template
        self.source_folder = args.source
        self.config = read_config(self.args.config)
        if self.args.glossary:
            self.glossary = read_glossary(self.args.glossary)

    def build(self):
        print "build deckset"
        with codecs.open(self.args.target, 'w+', 'utf-8') as self.target:
            with codecs.open(self.template_path, 'r', 'utf-8') as self.template:
                self._copy_template_header()

                self._append_section(self.config.get('title', 'title'))

                if 'introduction' in self.config:
                    self._append_section('introduction')

                # add all the groups
                for i, chapter in enumerate(self.config['chapter_order']):
                    self._append_section(chapter)

                if 'closing' in self.config:
                    self._append_section('closing')

                self._append_section(self.config.get('end', 'end'), skip_section_break=True)

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
        name = '%s.md' % make_pathname(name)
        with codecs.open(os.path.join(self.source_folder, name), 'r', 'utf-8') as section:
            for line in section:
                if line.strip() == GLOSSARY_MARKER:
                    r = DecksetGlossaryRenderer(self.glossary, self.target.write)
                    r.render()
                else:
                    self.target.write(line)
        if not skip_section_break:
            self.target.write('\n\n---\n\n')
