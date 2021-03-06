from __future__ import print_function
from __future__ import absolute_import

import re
from functools import partial
import logging

from .common import HEADLINE_PATTERN

logger = logging.getLogger(__name__)


class MetadataFilter(object):
    title = None
    summary = None
    metadata = None
    summary_lines = None

    METADATA_PATTERN = re.compile(r'\[\:(?P<key>.*?)\]: # \"(?P<value>.*?)\"')

    BEGIN_SUMMARY = "<summary>"
    END_SUMMARY = "</summary>"

    @classmethod
    def _header_filter(cls, line, after_metadata=False):
        """
        Read metadata up to (and including) first header.

        Metadata must be followed by a blank line!

        Transition to normal filter after headline.
        """
        if cls.METADATA_PATTERN.match(line.strip()) is not None:
            # process metadata
            match = cls.METADATA_PATTERN.match(line.strip())
            key = match.groupdict()['key']
            value = match.groupdict()['value']
            cls.metadata[key] = value
            return None, cls._header_filter

        elif line.strip().startswith('#'):
            # process header
            match = HEADLINE_PATTERN.search(line)
            try:
                cls.title = match.group('title')
            except AttributeError:
                logger.warning("title not set")
                cls.title = ''
            return line, cls._standard_filter

        elif line.strip() == '':
            # process empty line
            if after_metadata:
                return line, cls._standard_filter
            else:
                # ignore one blank line
                return None, partial(cls._header_filter, after_metadata=True)
        else:
            raise Exception('Metadata must be followed by an empty line!')

    @classmethod
    def _summary_filter(cls, line):
        """
        Read the summary and handle </summary>.

        Transition to standard filter after end of summary.
        """
        if line.strip() == cls.END_SUMMARY:
            return line, cls._standard_filter
        else:
            # remove bold around summary if present
            if line.startswith("**") or line.startswith("__"):
                sline = line.strip()[2:-2]
            else:
                sline = line
            cls.summary_lines.append(sline)
            cls.summary = '\n'.join(cls.summary_lines)

            return line, cls._summary_filter

    @classmethod
    def _standard_filter(cls, line):
        """
        Read and return all other input

        Transition to summary filter on encountering summary tag.
        """
        if line.strip() == cls.BEGIN_SUMMARY:
            return line, cls._summary_filter
        else:
            return line, cls._standard_filter

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
        # Initialize all class variables
        cls.title = None
        cls.summary = None
        cls.summary_lines = []
        cls.metadata = {}

        filter_function = cls._header_filter
        for line in lines:
            res, filter_function = filter_function(line)

            if res is not None:
                if not strip_summary_tags:
                    yield res
                elif res.strip() not in (cls.BEGIN_SUMMARY, cls.END_SUMMARY):
                    yield res
