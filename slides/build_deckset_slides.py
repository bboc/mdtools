#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Build the All Patterns Explained slide deck in Deckset format.
"""

import codecs

import os

from common import make_pathname, read_config


class DecksetWriter(object):
    CONTENT_MARKER = "<!-- INSERT-CONTENT -->"
    GROUP_INDEX_IMAGE = '\n![inline,fit](img/grouped-patterns/group-%s.png)\n\n'

    def __init__(self, args):
        self.args = args
        self.template_path = self.args.template
        self.source_folder = args.source
        self.config = read_config(self.args.config)

    def build(self):
        with codecs.open(self.args.target, 'w+', 'utf-8') as self.target:
            with codecs.open(self.template_path, 'r', 'utf-8') as self.template:
                self._copy_template_header()
                self._append_section('title.md')
                if 'introduction' in self.config:
                    self._append_section('introduction.md')

                # add all the groups
                for i, chapter in enumerate(self.config['chapter_order']):
                    self._append_section('%s.md' % make_pathname(chapter))

                if 'closing' in self.config:
                    self._append_section('closing.md')
                self._append_section('end.md', skip_section_break=True)

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
        with codecs.open(os.path.join(self.source_folder, name), 'r', 'utf-8') as section:
            for line in section:
                self.target.write(line)
        if not skip_section_break:
            self.target.write('\n\n---\n\n')

