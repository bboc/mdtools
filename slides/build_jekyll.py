#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Compile and preprocess all files so that jekyll can build a static (github) page out of it.
"""

import codecs
from collections import defaultdict
from functools import partial
import os
from operator import attrgetter
from textwrap import dedent

from common import markdown2html
from common import md_filename
import markdown_processor as mdp
import glossary
import macros

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


def nav_el(target, template, item):
    target.write(template % dict(name=item.title, path=item.slug))


class IndexMacro(object):
    """
    Process index macros.

    old code for index
    partial(mdp.insert_index, '<!-- GROUP-INDEX -->', self.config[CONTENT].chapters),
    partial(mdp.insert_index, '<!-- PATTERN-INDEX -->', self.config[CONTENT].index, summary_db=self.summary_db, format='html', sort=True),
    """

    @classmethod
    def render(cls, structure, format, *args, **kwargs):
        """Create a (sorted) index of pages.

        {{index:tag=pattern,sort=title}} create an index for all entries tagged 'pattern'
        {{index:root=slug}} create an index of all children of node
        sort and format default to None.
        root is processed before tag filter.

        # TODO: the structure module might be a better place for this
        """
        # get arguments
        tag_filter = kwargs.get('tag')
        sort = kwargs.get('sort')
        root = structure

        if 'root' in kwargs:
            root = kwargs['root']

        # select which nodes to show
        nodes_to_show = []
        if tag_filter:

            current_node = root
            while current_node:
                if tag_filter in current_node.tags:
                    nodes_to_show.append(current_node)
                current_node = current_node.successor
        else:
            nodes_to_show = root.children.copy()

        if sort:
            nodes_to_show.sort(key=attrgetter(sort))

        if format == 'html':
            return cls.render_html(nodes_to_show)
        else:  # plain list
            return cls.render_plain(nodes_to_show)

    INDEX_ELEMENT_PLAIN = "- [%(title)s](%(path)s.html)\n"

    @classmethod
    def render_plain(cls, nodes):
        res = []
        for node in nodes:
            res.append(cls.INDEX_ELEMENT_PLAIN % dict(title=node.title, path=node.slug))
        return '\n'.join(res)

    @classmethod
    def render_html(cls, nodes):
        res = ["<dl>"]
        for node in nodes:
            res.append(cls.html_index_element(node.title, node.slug, node.summary))
        res.append("</dl>")
        return '\n'.join(res)

    # TODO: enventually use dedent, but it messes up the diffs while the rewrite is in progress
    INDEX_ELEMENT_HTML = """
  <dt><a href="%(path)s.html">%(title)s</a></dt>
  <dd>%(summary)s</dd>"""

    @classmethod
    def html_index_element(cls, title, path, summary):
        if summary:
            summary = markdown2html(summary)
        else:
            summary = ''
        return cls.INDEX_ELEMENT_HTML % locals()


class JekyllWriter(object):
    GROUP_INDEX_IMAGE = '\n![inline,fit](img/grouped-patterns/group-%s.png)\n\n'

    def __init__(self, config, structure):
        self.cfg = config
        self.source_folder = self.cfg.source
        self.target_folder = self.cfg.target
        self.structure = structure
        self.glossary_renderer = glossary.JekyllGlossaryRenderer(9999)
        self.summary_db = defaultdict(list)

        # register all macros here
        macros.register_macro('full-glossary', partial(glossary.glossary_macro, glossary.JekyllGlossaryRenderer(9999)))
        macros.register_macro('index', partial(IndexMacro.render, self.structure, 'html'))

    def build(self):
        """Render the jekyll output.
        TODO: add index with summaries to each node that has children
        TODO: add index with summaries to all pattern group pages, to introduction and to appendix
        TODO: remove obsolete Templates
        TODO: create and insert glossary
        TODO: write pattern-index.md with all patterns and summaries
        TODO: write root index.md
        """

        self._build_chapters_overview()
        self._compile_front_matter()

        for part in self.structure.children:
            # TODO: process index
            self._build_chapter_index(part)
            if part.children:
                self._make_content_page(part)
                for chapter in part.children:
                    self._make_content_page(chapter)
                    # TODO: process index (maybe simply add one if the nod has children??)
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
            partial(macros.MacroFilter.filter),
            partial(mdp.add_glossary_term_tooltips, mdp.GLOSSARY_TERM_TOOLTIP_TEMPLATE),
        ]

    def _build_chapters_overview(self):
        """Build list of the chapters on the website from template. Already translation-aware."""
        # TODO: port or remove this
        print("_build_chapters_overview() not implemented")
        return

        with codecs.open(self.args.template, 'r', 'utf-8') as source:
            with codecs.open(os.path.join(self.target_folder, md_filename("index")), 'w+', 'utf-8') as target:
                processor = mdp.MarkdownProcessor(source, filters=[
                    partial(mdp.insert_index, '<!-- GROUP-INDEX -->', self.config[CONTENT].chapters),
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
                self._add_navigation(node, target)

    def _add_navigation(self, node, target):
        """Insert navigation for prev/up/next at the bottom of the page."""
        target.write("\n\n")

        next_item = node.successor
        if next_item:
            nav_el(target, NEXT_ELEMENT, next_item)
            target.write("<br/>")

        previous_item = node.predecessor
        if not node.parent.is_root():
            parent_item = node.parent
        else:
            parent_item = None

        # Skip previous if it is the parent item
        if previous_item and previous_item is not parent_item:
            nav_el(target, PREV_ELEMENT, previous_item)
            target.write("<br/>")

        # up: parent
        if not node.parent.is_root():
            nav_el(target, UP_ELEMENT, node.parent)
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
