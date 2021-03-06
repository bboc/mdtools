#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
import codecs
from string import Template
from textwrap import dedent

from .translate import translate as _

import regex as re


def cmd_build_index(args):
    cfg = get_config(args.config)
    if args.append:
        mode = 'a'
    else:
        mode = 'w+'
    with codecs.open(args.target, mode, 'utf-8') as target:
        if args.type == 'deckset':
            deckset_alphabetical_index(cfg[CONTENT].index, target)
        elif args.type == 'latex':
            latex_alphabetical_index(cfg[CONTENT].index, target)


def make_cell(items):
    return '<br\>'.join(items)


def deckset_alphabetical_index(section_index, target, per_page=20):
    """Create an alphabetical index of sections as a deckset table."""

    INDEX_ENTRY = Template("${title} - ${chapter_id}.${id}")
    INDEX_TABLE = Template(dedent("""
        %(sections)s $cont | %(sections)s %(cont)s
        --- | ---
        $left_content | $right_content
        """) % dict(sections=_("Patterns"), cont=_(u'(…)')))

    # sorting raw pattern data by name makes order independent of display format!
    section_index = sorted(section_index, key=lambda x: x.title.lower())
    sections = []
    for s in section_index:
        sections.append(INDEX_ENTRY.substitute(dict(title=s.title,
                                                    chapter_id=s.chapter_id,
                                                    id=s.id)))

    cont = ''

    def cut_sections(sections):
        return sections[:per_page], sections[per_page:]

    for idx in range(0, len(sections), per_page * 2):
        lgroup, sections = cut_sections(sections)
        if sections:
            rgroup, sections = cut_sections(sections)
        else:
            rgroup = []

        if cont:
            target.write("\n\n---\n\n")
        target.write(INDEX_TABLE.substitute(cont=cont,
                                            left_content=make_cell(lgroup),
                                            right_content=make_cell(rgroup)))
        cont = _(u'(…)')


WORD_CHARACTERS = re.compile(r'(?V1)[\W_--[-]]+', re.UNICODE)


def latex_alphabetical_index(section_index, target):
    """
    Create an alphabetical index of sections for LaTeX output.
    "[Rounds - 8.1](#pattern8.1:patternamewithoutspaces) \
    """
    # INDEX_ENTRY = Template("[${title}](#pattern${chapter_id}.${id}:${slug}) \\\n")
    INDEX_ENTRY = Template("[${title}](#${slug}) \\\n")

    # sorting raw pattern data by name makes order independent of display format!
    section_index = sorted(section_index, key=lambda x: x.title.lower())
    for s in section_index:

        item = INDEX_ENTRY.substitute(dict(title=s.title,
                                           chapter_id=s.chapter_id,
                                           id=s.id,
                                           slug=WORD_CHARACTERS.sub('', s.title.lower())))
        target.write(item)
