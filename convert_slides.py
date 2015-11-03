#!/usr/bin/python
 # -*- coding: utf-8 -*-

"""
Process markdown file into webpage content.
"""


from __future__ import unicode_literals

from glob import glob
import codecs
import os
import os.path


STATUS_TEMPLATE = """
=========================================
conversion finished

files processed: {0}
"""

IMG_TEMPLATE = '![](/static-images/{0}'

# TODO: make output of filename optional
# TODO: create line writer object with prev_line_empty 

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


def convert_to_web_cmd(args):
    print "starting conversion"
    convert_to_web(os.path.join(os.getcwd(), 'slides'), os.path.join(os.getcwd(), 'web'), args.footer)


def convert_to_web(slides_dir, target_dir, footer, slides_filename_pattern='*.md'):
    num_processed = 0 
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    
    for source_path in glob(os.path.join(slides_dir, slides_filename_pattern)):
        filename = os.path.basename(source_path)
        print 'converting', filename
        
        num_processed +=1
        
        result_path = os.path.join(target_dir, filename)

        with codecs.open(source_path, 'r', 'utf-8') as source:
            with codecs.open(result_path, 'w', 'utf-8') as target:
                lw = LineWriter(target, source.newlines)
                for line in source:
                    l = line.strip()    
                    if not l:
                        lw.mark_empty_line()
                    elif l == '---':
                        # omit line, do not change empty line marker!
                        pass 
                    elif l.startswith('#'):
                        lw.write(increase_headline_level(l))
                    elif line.lstrip().startswith("!["):
                        # fix image
                        pos = l.find('(')
                        lw.write(IMG_TEMPLATE.format(l[pos+1:]))
                    else:
                        lw.write(line)
                if footer:
                    target.write(footer)
    
    print STATUS_TEMPLATE.format(num_processed)


def increase_headline_level(line):
    line = '#' + line
    if line.endswith('#'):
        line = line + '#'
    return line

SLIDE_START = """
<section data-markdown>
    <script type="text/template">
"""

SLIDE_END = """    
    </script>
</section>
"""

REVEAL_IMG_TEMPLATE = '![]({0}'


def convert_to_reveal_cmd(args):
    print 'converting to reveal.js'

    with codecs.open(args.source, 'r', 'utf-8') as source:
        with codecs.open(args.target, 'w', 'utf-8') as target:

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


