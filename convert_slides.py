#!/usr/bin/python
 # -*- coding: utf-8 -*-

"""
Process markdown file into webpage content.

TODO: integrate with s3tools repository
"""

from __future__ import unicode_literals

from glob import glob
import codecs
import os
import os.path


class LineWriter(object):
    def __init__(self, target, newlines):
        self.target = target
        if not newlines:
            self.newlines = '\n'
        else:
            self.newlines = newlines
        self.prev_line_empty = False

    def write(self, line):
        """Write line to target, reset blank line counter, output newline if necessary."""
        if self.prev_line_empty:
            self.target.write(self.newlines)
        self.target.write(line.rstrip())
        self.target.write(self.newlines)
        self.prev_line_empty = False

    def mark_empty_line(self):
        self.prev_line_empty = True



SLIDE_START = """
<section data-markdown>
    <script type="text/template">
"""

SLIDE_END = """    
    </script>
</section>
"""

REVEAL_IMG_TEMPLATE = '![]({0}'


def convert_to_reveal(source,target):
    lw = LineWriter(target, source.newlines)
    lw.write(SLIDE_START)
    for line in source:
        l = line.strip()    
        if not l:
            lw.mark_empty_line()
        elif l == '---':
            lw.write(SLIDE_END)
            lw.write(SLIDE_START)
            # omit line, do not change empty line marker!
            pass 
        elif l.startswith('#'):
            lw.write(increase_headline_level(l))
        elif line.lstrip().startswith("!["):
            # fix image
            pos = l.find('(')
            lw.write(REVEAL_IMG_TEMPLATE.format(l[pos+1:]))
        else:
            lw.write(line)
    lw.write(SLIDE_END)


def convert_to_reveal_cmd(args):
    print 'converting to reveal.js'

    with codecs.open(args.source, 'r', 'utf-8') as source:
        with codecs.open(args.target, 'w', 'utf-8') as target:
            convert_to_reveal(source,target)
            


