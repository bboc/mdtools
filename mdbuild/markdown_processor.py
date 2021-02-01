#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import absolute_import
import logging
import re

from .common import SLIDE_MARKERS
from . import config
from .translate import translate as _

logger = logging.getLogger(__name__)


class MarkdownProcessor(object):
    """
    Process markdown through a series of filters cascaded into a pipeline.

    Usage:

    processor = MarkdownProcessor(source_file, filters = [
        # add filter functions in the order you want them to run
        partial(headline_prefix, prefix),
        partial(inject_glossary, glossary),
    )]
    # add another filter if you forgot one:
    processor.add_filter(partial(write,target))
    # apply all filters to stream:
    processor.process()
    """

    def __init__(self, input, filters=None):
        self.pipeline = input
        if filters:
            for f in filters:
                self.pipeline = f(self.pipeline)

    def add_filter(self, new_filter):
        """Add a filter to the pipeline."""
        self.pipeline = new_filter(self.pipeline)

    def process(self):
        """Process the stream."""
        for line in self.pipeline:
            pass


def dummy_filter(lines):
    """Basic structure of a filter.
    """
    for line in lines:
        yield line


def prefix_line(prefix, lines):
    for line in lines:
        yield "%s%s" % (prefix, line)


def write(target, lines):
    for line in lines:
        target.write(line)
        yield line


def prefix_headline(prefix, lines):
    """Prefix the first headline."""
    if prefix:
        line = next(lines)
        try:
            pos = line.index('# ')
        except ValueError:
            raise Exception(
                "no headline in first line (%s)" % line)
        yield ' '.join((line[:pos + 1], prefix, line[pos + 1:].lstrip()))
    for line in lines:
        yield line


def increase_all_headline_levels(level_increase, lines):
    """increase the level of ALL headlines."""
    for line in lines:
        if line.startswith('#'):
            yield ''.join(("#" * level_increase, line))
        else:
            yield line


IMG_PATTERN = re.compile("^\!\[(?P<caption>.*)\]\((?P<url>.*)\)")
DECKSET_IMAGE_COMMANDS = ['inline', 'fit', 'left', 'right', 'original', 'filtered']
IMG_TEMPLATE = '![%s](%s)'


def clean_images(lines):
    """Remove deckset formatters like "inline,fit" from images, skip background images ([fit])."""

    def clean_img(match):
        caption = match.group('caption')
        url = match.group('url')
        if caption.lower() == 'fit':
            # remove background image
            return ''
        else:
            for cmd in DECKSET_IMAGE_COMMANDS:
                if caption.lower().startswith(cmd):
                    # strip caption
                    return IMG_TEMPLATE % ('', url)
            else:
                # leave unchanged
                return IMG_TEMPLATE % (caption, url)

    for line in lines:
        yield IMG_PATTERN.sub(clean_img, line)


def clean_images_old(lines):
    """Remove deckset formatters like "inline,fit" from images, skip background images ([fit])."""
    for line in lines:
        if line.lstrip().startswith("!["):
            # fix image
            m = IMG_PATTERN.match(line)
            caption = m.group(2).lower()
            img_url = m.group(2)
            if caption.lower() == 'fit':
                yield '\n'
            else:
                yield '![](%s)\n' % img_url
        else:
            yield line


HEADLINE_PATTERN = re.compile("#{1,7} (?P<title>.*)")
FRONT_MATTER_TITLE = "title: \"%s\"\n"
FRONT_MATTER_SEPARATOR = "---\n"


def jekyll_front_matter(lines, params=None):
    line = next(lines)
    yield FRONT_MATTER_SEPARATOR
    match = HEADLINE_PATTERN.search(line)
    try:
        title = match.group('title')
    except AttributeError:
        pass
    else:
        # escape quotes in title
        yield FRONT_MATTER_TITLE % title.replace("\"", "\\\"")
        line = None
    if params:
        # insert parameters into front matter if present
        # preserve order of parameters to avoid random changes in files
        for key in sorted(params.keys()):
            yield ':'.join((key, params[key]))
    yield FRONT_MATTER_SEPARATOR
    yield "\n"

    if line:
        # first line wasn't a header
        yield line

    # add rest of stream
    for line in lines:
        yield line


BEGIN_SUMMARY = "<summary>"
END_SUMMARY = "</summary>"


def extract_summary(summary_db, name, lines):
    """Extracty summaries and add to summary_db, strip ** summary tags.

    Must come after replacing glossary entries so that the text is already expanded.
    """
    for line in lines:
        if line.strip() == BEGIN_SUMMARY:
            line = next(lines)
            while line.strip() != END_SUMMARY:
                # remove bold around summary if present
                if line.startswith("**"):
                    sline = line.strip()[2:-2]
                else:
                    sline = line
                summary_db[name].append(sline)
                yield line
                line = next(lines)
        else:
            yield line


STRIP_MODE = 'strip summary tags'


def summary_tags(lines, mode=STRIP_MODE):
    """
        Strip or translate summary tags:
        mode=None or mode=strip
    """
    for line in lines:
        if line.strip() == BEGIN_SUMMARY:
            if mode == STRIP_MODE:
                pass
        elif line.strip() == END_SUMMARY:
            if mode == STRIP_MODE:
                pass
        else:
            yield line


def unescape_macros(lines):
    """
    Unescape macros in templates.

    Jekyll variables also use two curly braces, so if a template uses
    a macro _and_ a Jekyll variable, the latter needs to be escaped.
    {{ site.url }} --> \{\{ site.url \}\}

    This filter reverts that escaping so that Jekyll can replace that
    variable.
    """
    for line in lines:
        line = line.replace('\{', '{')
        line = line.replace('\}', '}')
        yield line


class MetadataPlugin(object):
    title = None
    summary = None
    metadata = None

    METADATA_PATTERN = re.compile("\[\:(?P<key>.*?)\]: # \"(?P<value>.*?)\"")

    @classmethod
    def header_filter(cls, line):
        """
        Read metadata up (and including) first header.

        Transition to normal filter after headline.
        """
        if cls.METADATA_PATTERN.match(line.strip()) is not None:
            m = cls.METADATA_PATTERN.match(line.strip())
            key = m.groups()['key']
            value = m.groups()['value']
            cls.metadata[key] = value
            return None, cls.header_filter


    def summary_filter(cls): 
        """
        Read the summary and handle summary tags.

        Transition to standard filter after end of summary.
        """
        pass



    def standard_filter(cls):
        """
        Read all other input

        Transition to summary filter on encountering summary tag.

        """

    @classmethod
    def filter(cls, lines, strip_summary_tags=False):
        """
        Extract title, summary and other metadata.

        Metadata is stripped from the file so that this filter can be used to
        feed standard markdown to other filters down the line.

        Must come after replacing glossary entries so that the text in the summaries
        is already expanded.

        A metadata block must start at the top of the page, and is optionally followed
        by a blank line.

        [:author]: # "JohnDoe"

        see this question on stackoverflow for a discussion of metadata formats:

        https://stackoverflow.com/questions/44215896/markdown-metadata-format#44222826

        TODO: figure out if an object-based (not class-based) approach is a cleaner
            solution here?
        """
        cls.title = None
        cls.summary = None
        cls.metadata = {}

        summary = []


        # TODO: process metadata if present

        headline = next(lines)
        match = HEADLINE_PATTERN.search(headline)
        try:
            cls.title = match.group('title')
        except AttributeError:
            logger.warning("title not set")
            cls.title = ''
        yield headline
        for line in lines:
            if line.strip() == BEGIN_SUMMARY:
                if not strip_summary_tags:
                    yield line
                line = next(lines)
                while line.strip() != END_SUMMARY:
                    # remove bold around summary if present
                    if line.startswith("**") or line.startswith("__"):
                        sline = line.strip()[2:-2]
                    else:
                        sline = line
                    summary.append(sline)
                    yield line
                    line = next(lines)
                if not strip_summary_tags:
                    yield line
            else:
                yield line
        if summary:
            cls.summary = '\n'.join(summary)


SECTION_LINK_PATTERN = re.compile("\[(?P<title>[^\]]*)\]\(section:(?P<section>[^)]*)\)")
SECTION_LINK_TITLE_ONLY = "_%(title)s_"
SECTION_LINK_TO_HMTL = "[%(title)s](%(section)s.html)"
SECTION_LINK_TO_SLIDE = "_%(title)s_"


def convert_section_links(template, lines):
    """Convert section links for various output formats."""
    def link_replace(match):
        """Replace link with template."""
        data = {
            'title': match.group('title'),
            'section': match.group('section'),
        }
        return template % data

    for line in lines:
        line = SECTION_LINK_PATTERN.sub(link_replace, line)
        yield line


def remove_breaks_and_conts(lines):
    """
    Must be applied before jekyll_front_matter(), otherwise the front matter
    markers are removed.
    """
    for line in lines:
        if line.strip() in SLIDE_MARKERS:
            continue
        if line.strip().endswith(_(u"(…)")):
            continue
        yield line


TRANSLATION_MARKER = re.compile('\$\{_\("(?P<text>.*?)"\)\}')
PARAMETER_MARKER = re.compile('\$\{(?P<name>.*?)\}')


# TODO: rename to inject_variables_and_translations
# TODO: remove passing of config
def template(config, lines):
    """Insert translations und config parameters marked in the text like
    ${_("a string to translate")} or ${my_parameter}.
    """

    def insert_translation(match):
        text = match.group('text')
        return _(text, warnings=True)

    def insert_parameter(match):
        name = match.group('name')
        try:
            return getattr(config, name)
        except AttributeError:
            logger.error("Unknown config variable '%s" % name)
            return '${%s}' % name

    for line in lines:
        line = TRANSLATION_MARKER.sub(insert_translation, line)
        line = PARAMETER_MARKER.sub(insert_parameter, line)
        yield line
