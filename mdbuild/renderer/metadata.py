from __future__ import absolute_import

import re
from functools import partial
import logging
import markdown

from .common import HEADLINE_PATTERN

logger = logging.getLogger(__name__)


class MetadataFilter(object):
    """Process stream and extract/process metadata (title, summary etc.)"""

    # extracted metadata (acessed from outside)
    title = None
    summary = None
    metadata = None

    # store next filter function to use
    _filter_function = None

    # internal buffer for summary
    _summary_lines = None
    
    METADATA_PATTERN = re.compile(r'\[\:(?P<key>.*?)\]: # \"(?P<value>.*?)\"')
    YAML_METADATA_PATTERN = re.compile(r'(?P<key>.*?):\w+\"(?P<value>.*?)\"')
    
    METADATA_TEMPLATE = "%s: %s"

    BEGIN_SUMMARY = "<summary>"
    END_SUMMARY = "</summary>"

    SUMMARY_MARKUP = {
        'html': {
            BEGIN_SUMMARY: '<div class="card summary"><div class="card-body">',
            END_SUMMARY: '</div></div>\n',
        },    
        'epub': {
            BEGIN_SUMMARY: '<p class="summary">',
            END_SUMMARY: '</p>',
        },
        'latex': {
            BEGIN_SUMMARY: None,
            END_SUMMARY: None,
        },
        None: {
            BEGIN_SUMMARY: None,
            END_SUMMARY: '\n',
        },
        'preserve': {
            BEGIN_SUMMARY: BEGIN_SUMMARY,
            END_SUMMARY: END_SUMMARY,        
        }
    }

    @classmethod
    def _header_filter(cls, line, after_metadata=False):
        """
        Read metadata up to (and including) first header. Inject

        Metadata must be followed by a blank line!

        Transition to normal filter after headline.
        """
        if cls.METADATA_PATTERN.match(line.strip()) is not None:
            # process metadata
            match = cls.METADATA_PATTERN.match(line.strip())
            key = match.groupdict()['key']
            value = match.groupdict()['value']
            cls.metadata[key] = value
            cls._filter_function = cls._header_filter
            return None

        elif line.strip().startswith('#'):
            # process header
            match = HEADLINE_PATTERN.search(line)
            try:
                cls.title = match.group('title')
            except AttributeError:
                logger.warning("title not set")
                cls.title = ''
            cls._filter_function = cls._standard_filter
            return line

        elif line.strip() == '':
            # process empty line
            if after_metadata:
                cls._filter_function = cls._standard_filter
                return line
            else:
                # ignore one blank line
                cls._filter_function = partial(cls._header_filter, after_metadata=True)
                return None
        else:
            raise Exception('Metadata must be followed by an empty line!')


    @classmethod
    def _summary_filter(cls, line):
        """
        Read the summary and handle </summary>.

        Transition to standard filter after end of summary.
        """
        if line.strip() == cls.END_SUMMARY:
            cls._filter_function = cls._standard_filter
            return cls.SUMMARY_MARKUP[cls.target_format][cls.END_SUMMARY]
        else:
            # remove bold around summary if present
            if line.startswith("**") or line.startswith("__"):
                sline = line.strip()[2:-2]
            else:
                sline = line.strip()
            cls._summary_lines.append(sline)
            cls.summary = '\n'.join(cls._summary_lines)

            if cls.target_format == 'latex':
                # wrap summary in bold for latex (for now)
                # TODO: add LaTeX markup for a proper box or something nice
                if line.startswith("**") or line.startswith("__"):
                    pass
                else:
                    line = "**%s**\n\n" % line.strip()
            cls._filter_function = cls._summary_filter
            if cls.target_format == "html":
                # render to markdown (and strip <p>)
                return markdown.markdown(line)[3:-4] + "\n"
            else:
                return line

    @classmethod
    def _standard_filter(cls, line):
        """
        Read and return all other input

        Transition to summary filter on encountering summary tag.
        """
        if line.strip() == cls.BEGIN_SUMMARY:
            cls._filter_function = cls._summary_filter
            return cls.SUMMARY_MARKUP[cls.target_format][cls.BEGIN_SUMMARY]
        else:
            cls._filter_function = cls._standard_filter
            return line

    @classmethod
    def filter(cls, lines, target_format=None):
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

        Target Format:
            determines the output of metadata and summary tags
            html, epub: wrap summary in <p class=well-sm">
            latex: drop summary tag and wrap in ** if not already
            None (leave it as it is)
        """
        # Initialize all class variables
        cls.title = None
        cls.summary = None
        cls._summary_lines = []
        cls.metadata = {}
        cls.target_format = target_format

        if target_format not in cls.SUMMARY_MARKUP:
            raise Exception("Error: unknown target_format '%s'" % target_format)

        cls._filter_function = cls._header_filter
        for line in lines:
            res = cls._filter_function(line)
            if res is not None:
                yield res
