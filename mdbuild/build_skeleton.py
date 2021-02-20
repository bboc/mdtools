#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Build directory structure for source files.
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import

import codecs
import os
import re
from shutil import copyfile

from .common import create_directory, md_filename

from .build_revealjs_slides import RevealJsWriter, RevealJSBuilder
from .build_web_content import cmd_convert_to_web
from .revealjs_converter import RevealJsHtmlConverter




def main():
    # TODO: update parser 
    sp = subparsers.add_parser('skeleton',
                               help="Create skeleton directories and files for slides.")
    sp.add_argument('config', help='yaml file with presentation structure')
    sp.add_argument('target', help='Target directory for skeleton files.')
    sp.set_defaults(func=cmd_create_source_files_for_slides)






def build_reveal_slides(args):
    """
    Build reveal.js presentation. <target> is a file inside the reveal.js folder,
    template.html is expected in the same folder.
    """
    cw = RevealJSBuilder(args.config, args.source, args.glossary, args.glossary_items)
    rw = RevealJsWriter(args.target, args.template, cw)
    rw.build()


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
