#!/usr/bin/env python

from __future__ import absolute_import
import argparse

from .build_slides import cmd_build_slides, cmd_create_source_files_for_slides, cmd_convert_slides, cmd_compile_slides
from .index import cmd_build_index
from .template import cmd_template


def add_parser_compile(subparsers):
    """This is no longer needed."""
    sp = subparsers.add_parser('compile',
                               help="Compile and collect source files into one file per group/chapter.")
    sp.add_argument('config', help='yaml file with presentation structure')
    sp.add_argument('source', help='Directory with source files.')
    sp.add_argument('target', help='Target folder.')
    sp.add_argument('--chapter-title', default='none',
                    help='What kind of title slide to add to each chapter: text, img, both, none (default)')
    sp.add_argument('--add-chapter-illustration', action='store_true',
                    help='add chapter overview')
    sp.add_argument('--glossary', help='yaml file with glossary terms')
    sp.add_argument('--section-prefix', type=str, default='', help='string to prefix before each chapter headline, e.g. --section-prefix="Pattern %(chapter)s.%(section)s:" ')
    sp.add_argument('--no-section-prefix', action="store_true", default=False, help='Do not render any section prefixes')
    sp.set_defaults(func=cmd_compile_slides)


def add_parser_build(subparsers):
    """This is no longer needed."""
    sp = subparsers.add_parser('build',
                               help="Build a slide deck.")
    sp.add_argument('format', choices=['deckset', 'wordpress', 'revealjs', 'jekyll', "ebook"],
                    help="Output format (deckset | ebook | jekyll | revealjs | wordpress)")
    sp.add_argument('config', help='yaml file with presentation structure')
    sp.add_argument('source', help='Directory with source files.')
    sp.add_argument('target', help='Target file (for reveal.js and deckset) or folder (for wordpress or jekyll).')
    sp.add_argument('--footer', help='The footer to add to each group (wordpress output)')
    sp.add_argument('--template', help='The template to use (deckset, revealjs, and jekyll output)')
    sp.add_argument('--glossary', help='yaml file with glossary terms')
    sp.add_argument('--glossary-items', type=int, default=20, help='number of glossary items per page (used for deckset and revealjs)')
    sp.add_argument('--glossary-style', type=str, default='plain', help='glossary style for ebook builder (plain|footnotes|underline)')
    sp.add_argument('--section-prefix', type=str, default='', help='string to prefix before each chapter headline, e.g. --section-prefix="Pattern %(chapter)s.%(section)s:" ')
    sp.add_argument('--no-section-prefix', action="store_true", default=False, help='Do not render any section prefixes')
    sp.add_argument('--section-index-template', help='[jekyll] Template for the alphabetical section index page.')
    sp.add_argument('--introduction-template', help='[jekyll] Template for the introduction page.')

    sp.set_defaults(func=cmd_build_slides)


def add_parser_convert(subparsers):
    sp = subparsers.add_parser('convert',
                               help="Convert slides to reveal.js")
    sp.add_argument('source', help='Source presentation.')
    sp.add_argument('target', help='Target file (for reveal.js and deckset) or folder (for wordpress).')
    sp.add_argument('template', help='The template to use')
    sp.set_defaults(func=cmd_convert_slides)


# TODO: maybe port this command, move argument parser to code
def add_parser_skeleton(subparsers):
    sp = subparsers.add_parser('skeleton',
                               help="Create skeleton directories and files for slides.")
    sp.add_argument('config', help='yaml file with presentation structure')
    sp.add_argument('target', help='Target directory for skeleton files.')
    sp.set_defaults(func=cmd_create_source_files_for_slides)


def add_parser_build_index(subparsers):
    """This is probably no longer necessary."""
    sp = subparsers.add_parser('index',
                               help="Create an alphabetical index.")
    # \label{pattern1.10:proposalforming}

    sp.add_argument('type', help='Type of index (deckset|latex')
    sp.add_argument('config', help='yaml file with the document structure')
    sp.add_argument('-a', '--append', action="store_true", default=False)
    sp.add_argument('target')
    sp.set_defaults(func=cmd_build_index)


# TODO: port this command, , move argument parser to code
def add_parser_template(subparsers):
    sp = subparsers.add_parser('template',
                               help="Inject translations (and optionally parameters from a config) into a template file.")
    sp.add_argument('template', help='Source template')
    sp.add_argument('target', help='Filename for the resulting template')
    sp.add_argument('translations', help='gettext file')
    sp.add_argument('config', nargs='?', default=None, help="config file to read parameter values from")
    sp.set_defaults(func=cmd_template)


def get_parser():
    parser = argparse.ArgumentParser(
        description='Tools for creating and converting Markdown slide decks with Deckset and reveal.js',
        fromfile_prefix_chars='@'
    )
    parser.add_argument('--verbose', '-v', action='count')
    subparsers = parser.add_subparsers()
    add_parser_build(subparsers)
    add_parser_compile(subparsers)
    add_parser_convert(subparsers)
    add_parser_skeleton(subparsers)
    add_parser_build_index(subparsers)
    add_parser_template(subparsers)

    return parser


def main():
    # setup argparse

    parser = get_parser()
    args = parser.parse_args()
    args.func(args)
