#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Compile and preprocess all files so that jekyll can build a static (github) page out of it.
"""

import codecs
from collections import defaultdict
from functools import partial
import os
from textwrap import dedent

from common import md_filename
import markdown_processor as mdp
import glossary

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

    def __init__(self, config, structure):
        self.cfg = config
        self.source_folder = self.cfg.source
        self.target_folder = self.cfg.target
        self.structure = structure
        self.glossary_renderer = glossary.JekyllGlossaryRenderer(9999)
        self.summary_db = defaultdict(list)

    def build(self):
        self._build_chapters_overview()
        self._build_section_index()
        self._compile_front_matter()
        self._build_glossary()
        self._copy_appendix()

        for part in self.structure.parts:
            # TODO: process index
            self._build_chapter_index(part)
            if part.children:
                for chapter in part.children:
                    # TODO: process index
                    if chapter.children:
                        for section in chapter.children:
                            # TODO: process section
                            self._make_content_page(section)

    def common_filters(self):
        """Return the set of filters common to all pipelines."""
        return [
            mdp.remove_breaks_and_conts,
            partial(mdp.convert_section_links, mdp.SECTION_LINK_TO_HMTL),
            partial(mdp.inject_glossary),
            partial(mdp.add_glossary_term_tooltips, mdp.GLOSSARY_TERM_TOOLTIP_TEMPLATE),
        ]

    def _build_chapters_overview(self):
        """Build list of the chapters on the website from template. Already translation-aware."""
        # TODO: port or remove this
        print("TODO: _build_chapters_overview() not implemented")
        return

        with codecs.open(self.args.template, 'r', 'utf-8') as source:
            with codecs.open(os.path.join(self.target_folder, md_filename("index")), 'w+', 'utf-8') as target:
                processor = mdp.MarkdownProcessor(source, filters=[
                    partial(mdp.insert_index, '<!-- GROUP-INDEX -->', self.config[CONTENT].chapters),
                    partial(mdp.write, target),
                ])
                processor.process()

    def _build_section_index(self):
        """Build index of all sections from template. Already translation-aware."""
        # TODO: port or remove this
        print("_build_chapters_overview() not implemented")
        return

        with codecs.open(self.args.section_index_template, 'r', 'utf-8') as source:
            with codecs.open(os.path.join(self.target_folder, os.path.basename(self.args.section_index_template)), 'w+', 'utf-8') as target:
                processor = mdp.MarkdownProcessor(source, filters=[
                    partial(mdp.insert_index, '<!-- PATTERN-INDEX -->', self.config[CONTENT].index, summary_db=self.summary_db, format='html', sort=True),
                    partial(mdp.write, target),
                ])
                processor.process()

    def _build_chapter_index(self, chapter):

        # TODO: port or remove this
        print("_build_chapter_index() not implemented")
        return

        with codecs.open(os.path.join(self.target_folder, chapter.md_filename()), 'w+', 'utf-8') as target:
            target.write(mdp.FRONT_MATTER_SEPARATOR)
            target.write(mdp.FRONT_MATTER_TITLE % chapter.title)
            target.write(mdp.FRONT_MATTER_SEPARATOR)
            target.write('\n')

            # copy in chapter index
            chapter_index_file = os.path.join(self.source_folder, chapter.slug, 'index.md')
            if os.path.exists(chapter_index_file):
                with codecs.open(chapter_index_file, 'r', 'utf-8') as cif:
                    cif.next()  # skip headline
                    processor = mdp.MarkdownProcessor(cif, filters=self.common_filters())
                    processor.add_filter(partial(mdp.write, target))
                    processor.process()
                target.write('\n')

            # build section index
            for section in chapter.sections:
                target.write(mdp.html_index_element(section.title, section.slug, self.summary_db))
            self.chapter_navigation(target, chapter)

    def _compile_front_matter(self):
        # TODO: port or remove this
        print("_compile_front_matter() not implemented")
        return

        with codecs.open(os.path.join(self.target_folder, self.config[CONTENT].introduction.md_filename()), 'w+', 'utf-8') as target:
            with codecs.open(self.args.introduction_template, 'r', 'utf-8') as template:
                for line in template:
                    target.write(line)

            for item in self.config[CONTENT].introduction.sections:
                source_path = os.path.join(self.source_folder, self.config[CONTENT].introduction.slug, item.md_filename())
                with codecs.open(source_path, 'r', 'utf-8') as source:
                    processor = mdp.MarkdownProcessor(source, filters=self.common_filters())
                    processor.add_filter(partial(mdp.write, target))
                    processor.process()
                target.write('\n')
            self.intro_navigation(target)

    def _build_glossary(self):
        # TODO: port or remove this
        print("_build_glossary() not implemented")
        return

        with codecs.open(os.path.join(self.target_folder, md_filename("glossary")), 'w+', 'utf-8') as target:
            self.glossary_renderer.render(target.write)

    def _copy_appendix(self):
        """Copy all files in the appendix to individual files (skip glossary)."""
        # TODO: port or remove this
        print("_copy_appendix() not implemented")
        return

        for item in self.config[CONTENT].appendix.sections:
            if item.slug not in ['glossary', 'authors']:  # TODO: this should be a setting (maybe not glossary, but 'authors')
                self._copy_appendix_section(item.md_filename())

    def _copy_appendix_section(self, section_path):
        """Copy each section to a separate file."""
        # TODO: port or remove this
        source_path = os.path.join(self.source_folder, self.config[CONTENT].appendix.slug, section_path)
        target_path = os.path.join(self.target_folder, section_path)
        with codecs.open(source_path, 'r', 'utf-8') as source:
            with codecs.open(target_path, 'w+', 'utf-8') as target:
                processor = mdp.MarkdownProcessor(source, filters=self.common_filters())
                processor.add_filter(mdp.jekyll_front_matter)
                processor.add_filter(partial(mdp.write, target))
                processor.process()

    def _make_content_page(self, node):
        """Copy each section to a separate file."""
        # target_path = os.path.join(self.cfg.target, md_filename(node.relpath))
        target_path = os.path.join(self.cfg.target, md_filename(node.slug))

        with codecs.open(node.source_path, 'r', 'utf-8') as source:
            with codecs.open(target_path, 'w+', 'utf-8') as target:
                processor = mdp.MarkdownProcessor(source, filters=self.common_filters())
                processor.add_filter(mdp.jekyll_front_matter)
                # processor.add_filter(partial(mdp.prefix_headline, headline_prefix))
                processor.add_filter(partial(mdp.process_summary, mode=mdp.STRIP_MODE))
                processor.add_filter(partial(mdp.write, target))
                processor.process()
                # TODO: add navigation again
                # self.section_navigation(target, chapter, section)

    def section_navigation(self, target, chapter, section):
        """Insert prev/up/next."""
        # TODO: port or remove this        
        target.write("\n\n")

        # next link: next pattern, next group, or first group
        if section.id < len(chapter.sections):
            # next section in pattern (if any)
            next_item = chapter.sections[section.id]
        else:
            if section.chapter_id < len(self.config[CONTENT].chapters):
                # next chapter
                next_item = self.config[CONTENT].chapters[section.chapter_id]
            else:
                # last chapter: wrap around to first chapter index
                next_item = self.config[CONTENT].chapters[0]
        nav_el(target, NEXT_ELEMENT, next_item)
        target.write("<br/>")
        # prev link = prev pattern TODO: or prev group index (wrap around to last group)
        if section.id > 1:
            p_next = chapter.sections[section.id - 2]
            nav_el(target, PREV_ELEMENT, p_next)
            target.write("<br/>")
        # up: group index
        nav_el(target, UP_ELEMENT, chapter)
        target.write("\n\n")

    def chapter_navigation(self, target, chapter):
        """Insert prev/next."""
        # TODO: port or remove this        
        target.write("\n\n")

        # next link: always first pattern in group
        item = chapter.sections[0]
        nav_el(target, NEXT_ELEMENT, item)
        target.write("<br/>")
        # back:
        if chapter.id > 1:
            # last pattern of previous group
            target_chapter = self.config[CONTENT].chapters[chapter.id - 2]
        else:
            # last pattern of last group
            target_chapter = self.config[CONTENT].chapters[-1]
        item = target_chapter.sections[-1]
        nav_el(target, PREV_ELEMENT, item)
        target.write("\n\n")

    def intro_navigation(self, target):
        """Link to first group"""
        target.write("\n\n")
        item = self.config[CONTENT].chapters[0]
        nav_el(target, NEXT_ELEMENT, item)

        target.write("\n\n")


def nav_el(target, template, item):
    # TODO: port or remove this
    target.write(template % dict(name=item.title, path=item.slug))
