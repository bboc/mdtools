#!/usr/bin/env python

import argparse
import os
import shutil
import re
import os.path
import sys

from build_slides import cmd_build_slides, cmd_create_source_files_for_slides, cmd_convert_slides, cmd_compile_slides


def add_parser_compile(subparsers):
    sp = subparsers.add_parser('compile',
                               help="Compile and collect source files into one file per group/chapter.")
    sp.add_argument('config', help='yaml file with presentation structure')
    sp.add_argument('source', help='Directory with source files.')
    sp.add_argument('target', help='Target folder.')
    sp.add_argument('--chapter-title', default='none',
        help='What kind of title slide to add to each chapter: text, img, both, none (default)')
    sp.add_argument('--add-chapter-illustration', action='store_true',
        help='add chapter overview')
    sp.set_defaults(func=cmd_compile_slides)


def add_parser_build(subparsers):
    sp = subparsers.add_parser('build',
                               help="Build a slide deck.")
    sp.add_argument('format', help="presentation format, either 'deckset', 'wordpress' or 'revealjs'.")
    sp.add_argument('config', help='yaml file with presentation structure')
    sp.add_argument('source', help='Directory with source files.')
    sp.add_argument('target', help='Target file (for reveal.js and deckset) or folder (for wordpress).')
    sp.add_argument('--footer', help='The footer to add to each group (wordpress output)')
    sp.add_argument('--template', help='The template to use (deckset and revealjs output)')
    sp.set_defaults(func=cmd_build_slides)


def add_parser_convert(subparsers):
    sp = subparsers.add_parser('convert',
                               help="Convert slides to reveal.js")
    sp.add_argument('source', help='Source presentation.')
    sp.add_argument('target', help='Target file (for reveal.js and deckset) or folder (for wordpress).')
    sp.add_argument('template', help='The template to use')
    sp.set_defaults(func=cmd_convert_slides)
    

def add_parser_skeleton(subparsers):
    sp = subparsers.add_parser('skeleton',
                               help="Create skeleton directories and files for slides.")
    sp.add_argument('config', help='yaml file with presentation structure')
    sp.add_argument('target', help='Target directory for skeleton files.')
    sp.set_defaults(func=cmd_create_source_files_for_slides)


def main():
    # setup argparse
    parser = argparse.ArgumentParser(
        description='Tools for creating and converting Markdown slide decks with Deckset and reveal.js')
    parser.add_argument('--verbose', '-v', action='count')
    subparsers = parser.add_subparsers()
    add_parser_build(subparsers)
    add_parser_compile(subparsers)
    add_parser_convert(subparsers)
    add_parser_skeleton(subparsers)

    args = parser.parse_args()
    args.func(args)
