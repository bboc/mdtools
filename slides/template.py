#!/usr/bin/env python
# -*- coding: utf-8 -*-


import codecs
from functools import partial

from common import read_config
import markdown_processor as mdp
import translate


def cmd_template(args):

    # read translations
    translate.read_translation_memory(args.translations)
    if args.config:
        config = read_config(args.config)
    else:
        config = {}
    with codecs.open(args.template, 'r', 'utf-8') as source:
        with codecs.open(args.target, 'w+', 'utf-8') as target:
            processor = mdp.MarkdownProcessor(source, filters=[
                partial(mdp.template, config),
                partial(mdp.write, target),
            ])
            processor.process()
