#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Build directory structure for source files.
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import

import argparse
import codecs
import os

from .common import create_directory, md_filename


def main():
    parser = argparse.ArgumentParser(
        description='Create skeleton directories and files for a new project.',
        fromfile_prefix_chars='@'
    )

    parser.add_argument('--verbose', '-v', action='count', default=0)
    parser.add_argument('structure', help='yaml file with presentation structure')
    parser.add_argument('target', help='Target directory for skeleton files.')
    parser.set_defaults(func=cmd_create_source_files_for_slides)

    args = parser.parse_args()
    cmd_create_source_files_for_slides(args)


def cmd_create_source_files_for_slides(args):
    """
    Create dummy source files for slides. If file or folder exists, don't touch it.

    TODO: get this working again
    """

    create_directory(args.target)
    content = get_config(args.config)[CONTENT]

    def make_group(group):
        # create group dir
        group_root = os.path.join(args.target, group.slug)
        create_directory(group_root)
        # create group index file
        make_file(group_root, "index", group.title, '#')
        # create individual sections (add section name as headline)
        for section in group.sections:
            make_file(group_root, section, section, '##')

    def make_file(root, filename_root, title_root, markup='#'):
        """Create file if it does not exist."""
        filename = os.path.join(root, md_filename(filename_root))
        if not os.path.exists(filename):
            with codecs.open(filename, 'w+', 'utf-8') as fp:
                fp.write('%s %s\n\n' % (markup, make_title(title_root)))
        else:
            if args.verbose:
                print("skipped %s" % title_root)

    make_file(args.target, content.title, content.title)
    if content.introduction:
        make_group(content.introduction)
    for chapter in content.chapters:
        make_group(chapter)
    if content.appendix:
        make_group(content.appendix)
    if content.end:
        make_file(args.target, content.end, content.end)
