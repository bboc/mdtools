from __future__ import print_function
from __future__ import absolute_import

import re
import logging

from mdbuild.common import disable_exception_traceback
from mdbuild import config

from collections import namedtuple

logger = logging.getLogger(__name__)


class SkipOnlyFilter(object):
    """
    Process <skip> and <only> tags in the datastream.

    These tags can be nested:


    <skip formats="foo,bar" edition="baz" presets="boo">
        <only formats='foo'>
            some text
        </only>
    </skip>
     """

    State = namedtuple('State', ['pass_through', 'tag'])
    OPEN_TAG = re.compile(r"<(?P<tag>(skip)|(only))\s(?P<parameters>.*?)>")
    CLOSE_TAG = re.compile(r"</(?P<tag>(skip)|(only))>")
    PARAMETERS = re.compile(r"((formats=\"(?P<formats>.*?)\")|(editions=\"(?P<editions>.*?)\")|(presets=\"(?P<presets>.*?)\"))+")

    @classmethod
    def filter(cls, lines):
        # Initialize all class variables
        state = cls.State(pass_through=True, tag=None)
        cls.stack = []
        for line in lines:
            if cls.OPEN_TAG.match(line.strip()) is not None:
                # <skip …> or <only …>
                match = cls.OPEN_TAG.match(line.strip())
                tag = match.groupdict()['tag']
                # find and expand parameters
                parameters = match.groupdict()['parameters']
                match = cls.PARAMETERS.match(parameters)
                if match is None:
                    with disable_exception_traceback():
                        raise Exception("line does not compute: %s" % line)
                try:
                    presets = match.groupdict()['presets'].split(',')
                except AttributeError:
                    presets = []
                try:
                    editions = match.groupdict()['editions'].split(',')
                except AttributeError:
                    editions = []
                try:
                    formats = match.groupdict()['formats'].split(',')
                except AttributeError:
                    formats = []

                # first 'naive' guess at pass_through
                if tag == 'only':
                    pass_through = False
                    if config.cfg.preset in presets:
                        pass_through = True
                    if config.cfg.edition in editions:
                        pass_through = True
                    if config.cfg.target_format in formats:
                        pass_through = True
                elif tag == 'skip':
                    pass_through = True
                    if config.cfg.preset in presets:
                        pass_through = False
                    if config.cfg.edition in editions:
                        pass_through = False
                    if config.cfg.target_format in formats:
                        pass_through = False
                if not state.pass_through:
                    # if parent is blocking, this content is also blocked!
                    pass_through = False
                cls.stack.append(state)
                state = cls.State(pass_through=pass_through, tag=tag)
            elif cls.CLOSE_TAG.match(line.strip()) is not None:
                match = cls.CLOSE_TAG.match(line.strip())
                tag = match.groupdict()['tag']
                if tag == state.tag:
                    state = cls.stack.pop()
                else:
                    # mismatch in nested tags
                    if state.tag:
                        with disable_exception_traceback():
                            raise Exception("found </%s> inside \"%s\"-tag>" % (tag, state.tag))
                    else:
                        with disable_exception_traceback():
                            raise Exception("found mismatched </%s> " % tag)
            else:
                if state.pass_through:
                    yield line
