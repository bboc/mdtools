#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Compile and preprocess all files so that jekyll can build a static (github) page out of it.
"""

import codecs
from functools import partial
import os
from textwrap import dedent

from common import get_config, md_filename, make_headline_prefix
from common import FRONT_MATTER, APPENDIX, CHAPTERS, SECTIONS, SLUG, TITLE, CONTENT, ID, INDEX, CHAPTER_ID
import markdown_processor as mdp
from glossary import JekyllGlossaryRenderer, read_glossary

CHAPTER_INDEX_TEMPLATE = dedent("""
---
title: <!-- CHAPTER-NAME -->
---

<!-- CHAPTER-INTRO -->

<!-- SECTION-INDEX -->

""")


PREV_ELEMENT = "[&#9664; %(name)s](%(path)s.html)"
UP_ELEMENT = "[&#9650; %(name)s](%(path)s.html)"
NEXT_ELEMENT = "[&#9654; %(name)s](%(path)s.html)"


class JekyllWriter(object):
    GROUP_INDEX_IMAGE = '\n![inline,fit](img/grouped-patterns/group-%s.png)\n\n'

    def __init__(self, args):
        self.args = args
        self.source_folder = args.source
        self.target_folder = args.target
        self.config = get_config(self.args.config)
        self.glossary_renderer = JekyllGlossaryRenderer(self.args.glossary, 9999)
        self.glossary = read_glossary(self.args.glossary)

    def build(self):

        self._build_site_index()
        self._build_section_index()
        self._compile_front_matter()
        self._build_glossary()
        self._copy_appendix()

        # add all the chapters/sections
        for chapter in self.config[CONTENT][CHAPTERS]:
            self._build_chapter_index(chapter)
            for section in chapter[SECTIONS]:
                self._copy_section(chapter,
                                   section,
                                   make_headline_prefix(self.args, self.config, chapter[ID], section[ID]))

    def common_filters(self):
        """Return the set of filters common to all pipelines."""
        return [
            mdp.remove_breaks_and_conts,
            partial(mdp.convert_section_links, mdp.SECTION_LINK_TO_HMTL),
            partial(mdp.inject_glossary, self.glossary),
            partial(mdp.glossary_tooltip, self.glossary, mdp.GLOSSARY_TERM_TOOLTIP_TEMPLATE),
        ]

    def _build_site_index(self):
        """Build site index from template. Already translation-aware."""
        with codecs.open(self.args.template, 'r', 'utf-8') as source:
            with codecs.open(os.path.join(self.target_folder, md_filename("index")), 'w+', 'utf-8') as target:
                processor = mdp.MarkdownProcessor(source, filters=[
                    partial(mdp.insert_index, '<!-- GROUP-INDEX -->', self.config[CONTENT][CHAPTERS]),
                    partial(mdp.write, target),
                ])
                processor.process()

    def _build_section_index(self):
        """Build index of all sections from template. Already translation-aware."""
        with codecs.open(self.args.section_index_template, 'r', 'utf-8') as source:
            with codecs.open(os.path.join(self.target_folder, os.path.basename(self.args.section_index_template)), 'w+', 'utf-8') as target:
                processor = mdp.MarkdownProcessor(source, filters=[
                    partial(mdp.insert_index, '<!-- PATTERN-INDEX -->', self.config[INDEX], sort=True),
                    partial(mdp.write, target),
                ])
                processor.process()

    def _build_chapter_index(self, chapter):
        with codecs.open(os.path.join(self.target_folder, md_filename(chapter[SLUG])), 'w+', 'utf-8') as target:
            target.write(mdp.FRONT_MATTER_SEPARATOR)
            target.write(mdp.FRONT_MATTER_TITLE % chapter[TITLE])
            target.write(mdp.FRONT_MATTER_SEPARATOR)
            target.write('\n')

            # copy in chapter index
            chapter_index_file = os.path.join(self.source_folder, chapter[SLUG], 'index.md')
            if os.path.exists(chapter_index_file):
                with codecs.open(chapter_index_file, 'r', 'utf-8') as cif:
                    cif.next()  # skip headline
                    processor = mdp.MarkdownProcessor(cif, filters=self.common_filters())
                    processor.add_filter(partial(mdp.write, target))
                    processor.process()
                target.write('\n')

            # build section index
            for section in chapter[SECTIONS]:
                target.write(mdp.INDEX_ELEMENT % dict(name=section[TITLE],
                                                      path=section[SLUG]))
            self.chapter_navigation(target, chapter)

    def _compile_front_matter(self):
        with codecs.open(os.path.join(self.target_folder, md_filename(FRONT_MATTER)), 'w+', 'utf-8') as target:
            with codecs.open(self.args.introduction_template, 'r', 'utf-8') as template:
                for line in template:
                    target.write(line)

            for item in self.config[CONTENT][FRONT_MATTER][SECTIONS]:
                source_path = os.path.join(self.source_folder, FRONT_MATTER, md_filename(item[SLUG]))
                with codecs.open(source_path, 'r', 'utf-8') as source:
                    processor = mdp.MarkdownProcessor(source, filters=self.common_filters())
                    processor.add_filter(partial(mdp.write, target))
                    processor.process()
                target.write('\n')
            self.intro_navigation(target)

    def _build_glossary(self):
        with codecs.open(os.path.join(self.target_folder, md_filename("glossary")), 'w+', 'utf-8') as target:
            self.glossary_renderer.render(target.write)

    def _copy_appendix(self):
        """Copy all files in the appendix to individual files (skip glossary)."""
        for item in self.config[CONTENT][APPENDIX][SECTIONS]:
            if item[SLUG] not in ['glossary', 'authors']:  # TODO: this should be a setting (maybe not glossary, but 'authors')
                self._copy_appendix_section(md_filename(item[SLUG]))

    def _copy_appendix_section(self, section_path):
        """Copy each section to a separate file."""
        source_path = os.path.join(self.source_folder, APPENDIX, section_path)
        target_path = os.path.join(self.target_folder, section_path)
        with codecs.open(source_path, 'r', 'utf-8') as source:
            with codecs.open(target_path, 'w+', 'utf-8') as target:
                processor = mdp.MarkdownProcessor(source, filters=self.common_filters())
                processor.add_filter(mdp.jekyll_front_matter)
                processor.add_filter(partial(mdp.write, target))
                processor.process()

    def _copy_section(self, chapter, section, headline_prefix):
        """Copy each section to a separate file."""
        source_path = os.path.join(self.source_folder, chapter[SLUG], md_filename(section[SLUG]))
        target_path = os.path.join(self.target_folder, md_filename(section[SLUG]))
        with codecs.open(source_path, 'r', 'utf-8') as source:
            with codecs.open(target_path, 'w+', 'utf-8') as target:
                processor = mdp.MarkdownProcessor(source, filters=self.common_filters())
                processor.add_filter(mdp.jekyll_front_matter)
                # processor.add_filter(partial(mdp.prefix_headline, headline_prefix))
                processor.add_filter(partial(mdp.write, target))
                processor.process()
                self.section_navigation(target, chapter, section)

    def section_navigation(self, target, chapter, section):
        """Insert prev/up/next."""
        target.write("\n\n")

        # next link: next pattern, next group, or first group
        if section[ID] < len(chapter[SECTIONS]):
            # next section in pattern (if any)
            next_item = chapter[SECTIONS][section[ID]]
        else:
            if section[CHAPTER_ID] < len(self.config[CONTENT][CHAPTERS]):
                # next chapter
                next_item = self.config[CONTENT][CHAPTERS][section[CHAPTER_ID]]
            else:
                # last chapter: wrap around to first chapter index
                next_item = self.config[CONTENT][CHAPTERS][0]
        nav_el(target, NEXT_ELEMENT, next_item)
        target.write("<br/>")
        # prev link = prev pattern TODO: or prev group index (wrap around to last group)
        if section[ID] > 1:
            p_next = chapter[SECTIONS][section[ID] - 2]
            nav_el(target, PREV_ELEMENT, p_next)
            target.write("<br/>")
        # up: group index
        nav_el(target, UP_ELEMENT, chapter)
        target.write("\n\n")

    def chapter_navigation(self, target, chapter):
        """Insert prev/next."""
        target.write("\n\n")

        # next link: always first pattern in group
        item = chapter[SECTIONS][0]
        nav_el(target, NEXT_ELEMENT, item)
        target.write("<br/>")
        # back:
        if chapter[ID] > 1:
            # last pattern of previous group
            target_chapter = self.config[CONTENT][CHAPTERS][chapter[ID] - 2]
        else:
            # last pattern of last group
            target_chapter = self.config[CONTENT][CHAPTERS][-1]
        item = target_chapter[SECTIONS][-1]
        nav_el(target, PREV_ELEMENT, item)
        target.write("\n\n")

    def intro_navigation(self, target):
        """Link to first group"""
        target.write("\n\n")
        item = self.config[CONTENT][CHAPTERS][0]
        nav_el(target, NEXT_ELEMENT, item)

        target.write("\n\n")


def nav_el(target, template, item):
    target.write(template % dict(name=item[TITLE], path=item[SLUG]))
