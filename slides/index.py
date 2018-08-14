#!/usr/bin/env python
# -*- coding: utf-8 -*-

import yaml
import codecs
from collections import defaultdict
from operator import itemgetter
from string import Template
from textwrap import dedent

from common import make_title, read_config, md_filename, CHAPTERS, CHAPTER_ORDER
from translate import translate as _


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


def read_index_db(index_file):
    """Create read index from index.yaml and provide a sorted data structure:

    index = {
        'groups': [group1, group2, ] # ordered by group number
        'patterns-by-group': { # used to create group index files
            'group1-path': [ pattern1, pattern2] # ordered by pattern order in group
        }
        'group-by-path': {  # used to build navigation
            'group-path': group,
        }
        'groups-by-gid': {
            gid: group
        }
    }
    groups and patterns are simple dictionaries.
    """

    index = read_config(index_file)

    index['groups'].sort(key=itemgetter('gid'))

    index['groups-by-gid'] = {}
    index['group-by-path'] = {}
    for group in index['groups']:
        index['group-by-path'][group['path']] = group
        index['groups-by-gid'][group['gid']] = group

    # build patterns by group
    index['patterns-by-group'] = defaultdict(list)

    for pattern in index['patterns']:
        gp = index['groups-by-gid'][pattern['gid']]['path']
        index['patterns-by-group'][gp].append(pattern)

    for gp in index['group-by-path'].keys():
        index['patterns-by-group'][gp].sort(key=itemgetter('pid'))

    return index


def make_cell(items):
    return '<br\>'.join(items)


def deckset_alphabetical_index(pattern_data, target, per_page=20):
    """Create an alphabetical index of patterns as a deckset table."""

    INDEX_ENTRY = Template("$name - $gid.$pid")
    INDEX_TABLE = Template(dedent("""
        %(patterns)s $cont | %(patterns)s %(cont)s
        --- | ---
        $left_content | $right_content
        """) % dict(patterns=_("Patterns"), cont=_(u'(…)')))

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
        cont = _(u'(…)')
