#!/usr/bin/env python
# -*- coding: utf-8 -*-

import yaml
import codecs
from operator import itemgetter
from string import Template
from textwrap import dedent

from common import make_title, read_config, md_filename, CHAPTERS, CHAPTER_ORDER


def cmd_build_index_db(args):
    """
    Build a yaml file with all chapters and their IDs (chapter and section ID.
    """

    with open(args.config, "r") as source:
        config = yaml.load(source)

    patterns = []
    groups = []
    for gid, group in enumerate(config[CHAPTER_ORDER], 1):
        groups.append(dict(name=make_title(group), gid=gid, path=md_filename(group)))
        for pid, pattern in enumerate(config[CHAPTERS][group], 1):
            patterns.append(dict(name=make_title(pattern), gid=gid, pid=pid, path=md_filename(pattern)))

    with codecs.open(args.index_db, 'w', 'utf-8') as target:
        yaml.dump(dict(patterns=sorted(patterns, key=itemgetter('name')),
                  groups=sorted(groups, key=itemgetter('name'))),
                  target,
                  default_flow_style=False)


def cmd_build_deckset_index(args):
    c = read_config(args.index_db)
    with codecs.open(args.target, 'a', 'utf-8') as target:
        deckset_alphabetical_index(c['patterns'], target)


def make_cell(items):
    return '<br\>'.join(items)


def deckset_alphabetical_index(pattern_data, target, per_page=20):
    """Create an alphabetical index of patterns as a deckset table."""

    INDEX_ENTRY = Template("$name - $gid.$pid")
    INDEX_TABLE = Template(dedent("""
        Patterns $cont | Patterns (cont.)
        --- | ---
        $left_content | $right_content
        """))

    # sorting raw pattern data by name makes order independent of display format!
    pattern_data = sorted(pattern_data, key=lambda x: x['name'].lower())
    patterns = [INDEX_ENTRY.substitute(p) for p in pattern_data]

    cont = ''

    def cut_patterns(patterns):
        return patterns[:per_page], patterns[per_page:]

    for idx in range(0, len(patterns), per_page * 2):
        lgroup, patterns = cut_patterns(patterns)
        if patterns:
            rgroup, patterns = cut_patterns(patterns)
        else:
            rgroup = []

        if cont:
            target.write("\n\n---\n\n")
        target.write(INDEX_TABLE.substitute(cont=cont,
                                            left_content=make_cell(lgroup),
                                            right_content=make_cell(rgroup)))
        cont = "(cont.)"
