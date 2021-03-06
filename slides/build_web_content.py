#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Process markdown file into webpage content.
"""


from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import

from glob import glob
import codecs
import os
import os.path
import sys

from .common import LineWriter, SLIDE_MARKERS
from .glossary import GLOSSARY_MARKER, WordpressGlossaryRenderer
from .translate import translate as _


STATUS_TEMPLATE = """
=========================================
conversion finished

files processed: {0}
"""

IMG_TEMPLATE = '![](/static-images/{0}'

# TODO: make output of filename optional
# TODO: create line writer object with prev_line_empty


def cmd_convert_to_web(args):
    # print "starting conversion"

    with codecs.open(args.footer, 'r', 'utf-8') as ft:
        footer = ft.read()

    glossary_renderer = WordpressGlossaryRenderer(args.glossary)
    # TODO: add increase headline level as commandline option
    convert_to_web(args.source, args.target, footer, glossary_renderer, False)


def convert_to_web(source, target, footer, glossary_renderer, increase_headline_level=False):

    num_processed = 0
    if os.path.isfile(source):
        # process one file
        if os.path.isdir(target):
            result_path = os.path.join(target, os.path.basename(source))
        else:
            result_path = target

            convert_file_for_web(source, result_path, footer, glossary_renderer)
            num_processed += 1

    elif os.path.isdir(source):
        # source is a directory: process all files inside
        if os.path.exists(target):
            if not os.path.isdir(target):
                print("target exsists but is not a directory.")
                sys.exit(1)
        else:
            os.makedirs(target)

        SOURCE_FILENAME_PATTERN = '*.md'

        for source_path in glob(os.path.join(source, SOURCE_FILENAME_PATTERN)):
            filename = os.path.basename(source_path)
            # print 'converting', filename
            result_path = os.path.join(target, filename)
            convert_file_for_web(source_path, result_path, footer, glossary_renderer, increase_headline_level)
            num_processed += 1

    # print STATUS_TEMPLATE.format(num_processed)


def convert_file_for_web(source_path, result_path, footer, glossary_renderer, increase_headline_level):

    with codecs.open(source_path, 'r', 'utf-8') as source:
        with codecs.open(result_path, 'w', 'utf-8') as target:
            lw = LineWriter(target, source.newlines)
            for line in source:
                L = line.strip()
                if not L:
                    lw.mark_empty_line()
                elif L == GLOSSARY_MARKER:
                    glossary_renderer.render(lw.write)
                elif L in SLIDE_MARKERS:
                    # omit line, do not change empty line marker!
                    pass
                elif L.startswith('#'):
                    if L.endswith(_(u'(…)')):
                        pass  # omit slides with continued headlines
                    else:
                        if increase_headline_level:
                            lw.write(increase_headline_level(L))
                        else:
                            lw.write(line)
                elif line.lstrip().startswith("!["):
                    # fix image
                    pos = L.find('(')
                    lw.write(IMG_TEMPLATE.format(L[pos + 1:]))
                else:
                    lw.write(line)
            if footer:
                target.write(footer)
