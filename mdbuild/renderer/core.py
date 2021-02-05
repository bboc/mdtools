#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import absolute_import

import logging

logger = logging.getLogger(__name__)


class Renderer(object):
    """
    Process text files through a series of filters cascaded into a pipeline.

    Usage:

    renderer = Renderer(source_file, filters = [
        # add filter functions in the order you want them to run
        partial(headline_prefix, prefix),
        partial(inject_glossary, glossary),
    )]
    # add another filter if you forgot one:
    renderer.add_filter(partial(write,target))
    # apply all filters to stream:
    renderer.render()
    """

    def __init__(self, input, filters=None):
        self.pipeline = input
        if filters:
            for f in filters:
                self.pipeline = f(self.pipeline)

    def add_filter(self, new_filter):
        """Add a filter to the pipeline."""
        self.pipeline = new_filter(self.pipeline)

    def render(self):
        """Process the stream."""
        for line in self.pipeline:
            pass
