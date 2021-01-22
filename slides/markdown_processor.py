#!/usr/bin/python
# -*- coding: utf-8 -*-

from operator import attrgetter
import re

from common import SLIDE_MARKERS, escape_html_delimiters, markdown2html
from config import TITLE
from glossary import GLOSSARY_MARKER
from translate import translate as _


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
        line = lines.next()
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
        """Get a definition of a term from the glossary."""
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


HEADLINE_PATTERN = re.compile("#{0,7} (?P<title>.*)")
FRONT_MATTER_TITLE = "title: \"%s\"\n"
FRONT_MATTER_SEPARATOR = "---\n"


def jekyll_front_matter(lines, params=None):
    # TODO: raise exception if no headline in first line of file!!!
    line = lines.next()
    yield FRONT_MATTER_SEPARATOR
    match = HEADLINE_PATTERN.search(line)
    title = match.group('title')
    yield FRONT_MATTER_TITLE % title
    if params:
        # insert parameters into front matter if present
        # preserve order of parameters to avoid random changes in files
        for key in sorted(params.keys()):
            yield ':'.join((key, params[key]))
    yield FRONT_MATTER_SEPARATOR
    yield "\n"

    # add rest of stream
    for line in lines:
        yield line


DEFINE_PATTERN = re.compile("\{\{define\:(?P<name>.*)\}\}")
GLOSSARY_PATTERN = re.compile("\{\{glossary\:(?P<name>.*)\}\}")


def inject_glossary(glossary, lines):
    """Expand glossary terms and definitions.
    """
    def glossary_replace(match, key, pattern):
        """Get a definition of a term from the glossary."""
        name = match.group('name')
        try:
            return pattern % glossary['terms'][name][key]
        except KeyError:
            print('cant find ', key, " for glossary entry ", name)
            raise

    def insert_definition(match):
        return glossary_replace(match, 'definition', "_%s_")

    def insert_glossary_term(match):
        return glossary_replace(match, 'glossary', "%s")

    for line in lines:
        if glossary:
            # replace definitions from glossary
            line = DEFINE_PATTERN.sub(insert_definition, line)
            line = GLOSSARY_PATTERN.sub(insert_glossary_term, line)
        yield line


BEGIN_SUMMARY = "<summary>"
END_SUMMARY = "</summary>"


def extract_summary(summary_db, name, lines):
    """Extracty summaries and add to summary_db, strip ** summary tags.

    Must come after inject_glossary so that the text is already expanded.
    """
    for line in lines:
        if line.strip() == BEGIN_SUMMARY:
            line = lines.next()
            while line.strip() != END_SUMMARY:
                # remove bold around summary if present
                if line.startswith("**"):
                    sline = line.strip()[2:-2]
                else:
                    sline = line
                summary_db[name].append(sline)
                yield line
                line = lines.next()
        else:
            yield line


STRIP_MODE = 'strip summary tags'


def process_summary(lines, mode=STRIP_MODE):
    """Process summary tags:
    mode=None or mode=strip
    Strip summary tags from output."""
    for line in lines:
        if line.strip() == BEGIN_SUMMARY:
            if mode == STRIP_MODE:
                pass
        elif line.strip() == END_SUMMARY:
            if mode == STRIP_MODE:
                pass
        else:
            yield line


GLOSSARY_TERM_PATTERN = re.compile("\[(?P<title>[^\]]*)\]\(glossary:(?P<glossary_term>[^)]*)\)")

GLOSSARY_TERM_TOOLTIP_TEMPLATE = """<dfn data-info="%(name)s: %(description)s">%(title)s</dfn>"""


def add_glossary_term_tooltips(glossary, template, lines):
    """Add tooltip for marked glossary entries."""
    def glossary_replace(match):
        """Replace term with glossary tooltip or other template."""
        term = match.group('glossary_term')
        description = glossary['terms'][term]['glossary']
        description = escape_html_delimiters(description)
        data = {
            'title': match.group('title'),
            'name': glossary['terms'][term]['name'],
            'description': description,
        }
        return template % data

    for line in lines:
        line = GLOSSARY_TERM_PATTERN.sub(glossary_replace, line)
        yield line


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


def insert_glossary(renderer, lines):
    """Insert full glossary when GLOSSARY_MARKER is encountered."""

    glossary_contents = []

    def callback(text):
        glossary_contents.append(text)

    for line in lines:
        if line.strip() == GLOSSARY_MARKER:
            renderer.render(callback)
            callback('\n')
            yield '\n'.join(glossary_contents)
        else:
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


INDEX_ELEMENT = "- [%(name)s](%(path)s.html)\n"
INDEX_ELEMENT_HTML = """
  <dt><a href="%(path)s.html">%(name)s</a></dt>
  <dd>%(summary)s</dd>
"""


def html_index_element(name, path, summary_db):
    summary = markdown2html("".join(summary_db[path]))
    return INDEX_ELEMENT_HTML % locals()


def insert_index(marker, items, lines, sort=False, summary_db=None, format=None):
    """
    Insert an index as markdown-links, can be used for groups and sections.
    Items is a list of dictionaries with keys path and name.
    """
    if sort:
        items.sort(key=attrgetter(TITLE))
    for line in lines:
        if line.strip() == marker:
            if format == 'html':
                yield "<dl>"
                for item in items:
                    yield html_index_element(item.title, item.slug, summary_db)
                yield "</dl>"
            else:  # plain list
                for item in items:
                    yield INDEX_ELEMENT % dict(name=item.title, path=item.slug)

        else:
            yield line


TRANSLATION_MARKER = re.compile('\$\{_\("(?P<text>.*?)"\)\}')
PARAMETER_MARKER = re.compile('\$\{(?P<name>.*?)\}')


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
            return config[name]
        except KeyError:
            print "ERROR: Unknown Parameter", name
            return "${%s}" % name

    for line in lines:
        line = TRANSLATION_MARKER.sub(insert_translation, line)
        line = PARAMETER_MARKER.sub(insert_parameter, line)
        yield line
