"""
Command line interface to difflib.py which wraps ndiff output in Critic Markup syntax.
"""

import sys
import os
import time
import difflib
import optparse


DELETED = '- '  # line unique to sequence 1
ADDED = '+ '   # line unique to sequence 2
COMMON = '  '  # line common to both sequences
NEITHER = '? '  # line not present in either input sequence

CM_ADD = '{++%s++}%s'
CM_DEL = '{--%s--}%s'
CM_HI = '{==%s==}{>>intraline differences<<}%s'
PLAIN = '%s%s'

LE_NL = '\n'
LE_CRNL = '\r\n'


def critic_markup(lines):
    "wrap lines of ndiff output in critic markup"
    while True:
        line = next(lines)
        try:
            template, content, line_ending = parse_line(line)
            yield template % (content, line_ending)
        except IntralineDifferences:
            pass  # suppress intraline difference markers


class IntralineDifferences(Exception):
    pass


def parse_line(line):
    """Parse line into diff marker, contents and line_ending (if applicable)"""
    if line.startswith(ADDED):
        template = CM_ADD
        content = line[2:]
    elif line.startswith(DELETED):
        template = CM_DEL
        content = line[2:]
    elif line.startswith(NEITHER):
        raise IntralineDifferences()
    elif line.startswith(COMMON):
        template = PLAIN
        content = line[2:]
    else:
        raise Exception("NO MARKER::%s" % line)

    if line.endswith(LE_NL):
        line_ending = LE_NL
        content = content[:-1]
    elif line.endswith(LE_CRNL):
        line_ending = LE_CRNL
        content = content[:-2]
    else:
        line_ending = ''

    return template, content, line_ending


def main():
     # Configure the option parser
    usage = "Output differences between two files as CriticMarkup. Output is a full file, works on full paragraphs only. \nusage: %prog [options] fromfile tofile"
    parser = optparse.OptionParser(usage)
    (options, args) = parser.parse_args()

    if len(args) == 0:
        parser.print_help()
        sys.exit(1)
    if len(args) != 2:
        parser.error("need to specify both a fromfile and tofile")

    fromfile, tofile = args  # as specified in the usage string

    # we're passing these as arguments to the diff function
    fromdate = time.ctime(os.stat(fromfile).st_mtime)
    todate = time.ctime(os.stat(tofile).st_mtime)
    fromlines = open(fromfile, 'U').readlines()
    tolines = open(tofile, 'U').readlines()

    diff = difflib.ndiff(fromlines, tolines)
    # diff is a generator
    sys.stdout.writelines(critic_markup(diff))

if __name__ == '__main__':
    main()
