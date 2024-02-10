
import logging
import re
import sys

from mdbuild.common import SLIDE_MARKERS
from mdbuild import config
from mdbuild.translate import translate as _

from .common import HEADLINE_PATTERN

# make other filters from this package available here:
from .skiponly import SkipOnlyFilter
from .metadata import MetadataFilter

logger = logging.getLogger(__name__)


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


IMG_PATTERN = re.compile(r'^\!\[(?P<caption>.*)\]\((?P<url>.*)\)')
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


FRONT_MATTER_TITLE = "title: \"%s\"\n"
FRONT_MATTER_SEPARATOR = "---\n"


def jekyll_front_matter(metadata, lines):
    """
    Inject Jekyll front matter.

    TODO: this should use the library for yaml, instead of handcrafted lines of text!
    """
    
    def escape_quotes(text):
        return text.replace("\"", "\\\"")

    line = next(lines)
    yield FRONT_MATTER_SEPARATOR
    match = HEADLINE_PATTERN.search(line)
    try:
        title = match.group('title')
    except AttributeError:
        pass
    else:
        # escape quotes in title
        yield FRONT_MATTER_TITLE % escape_quotes(title)
        line = None
    if metadata:
        # insert parameters into front matter if present
        # preserve order of parameters to avoid random changes in files
        for key in sorted(metadata.keys()):
            yield '%s: "%s"\n' % (key, escape_quotes(metadata[key]))
    yield FRONT_MATTER_SEPARATOR
    yield "\n"

    if line:
        # first line wasn't a header
        yield line

    # add rest of stream
    for line in lines:
        yield line


def unescape_macros(lines):
    r"""
    Unescape macros in templates.

    Jekyll variables also use two curly braces, so if a template uses
    a macro _and_ a Jekyll variable, the latter needs to be escaped.
    {{ site.url }} --> \{\{ site.url \}\}

    This filter reverts that escaping so that Jekyll can replace that
    variable.
    """
    for line in lines:
        line = line.replace(r'\{', '{')
        line = line.replace(r'\}', '}')
        yield line


SECTION_LINK_PATTERN = re.compile(r'\[(?P<title>[^\]]*)\]\(section:(?P<section>[^)]*)\)')

SECTION_LINK_TEMPLATES = {
    'title': "_%(title)s_",
    'html': "[%(title)s](%(section)s.html)",
    'slides': "_%(title)s_"
}


def convert_section_links(style, lines):
    """Convert section links for various output formats."""
    try:
        template = SECTION_LINK_TEMPLATES[style]
    except KeyError:
        logger.error('unknown section link style "%s"' % style)
        sys.exit(1)

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


TRANSLATION_MARKER = re.compile(r'\$\{_\("(?P<text>.*?)"\)\}')
PARAMETER_MARKER = re.compile(r'\$\{(?P<name>.*?)\}')


def inject_variables_and_translations(lines):
    """
    Insert translations und config parameters marked in the text like
    ${_("a string to translate")} or ${my_parameter}.
    """

    def insert_translation(match):
        text = match.group('text')
        return _(text, warnings=True)

    def insert_parameter(match):
        name = match.group('name')
        try:
            return getattr(config.cfg.variables, name)
        except AttributeError:
            logger.error("Unknown config variable '%s" % name)
            return '${%s}' % name

    for line in lines:
        line = TRANSLATION_MARKER.sub(insert_translation, line)
        line = PARAMETER_MARKER.sub(insert_parameter, line)
        yield line
