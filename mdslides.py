# -*- coding: utf-8 -*-

import argparse

from convert_slides import convert_to_web_cmd, convert_to_reveal_cmd

def dir_type(dirname):
    # type for argparse
    if os.path.isdir(dirname):
        return os.path.normpath(dirname)
    raise argparse.ArgumentTypeError('%s is not a valid directory' % dirname)


def get_parser():
    parser = argparse.ArgumentParser(
        description='Convert slide decks to other formats')

    parent = argparse.ArgumentParser(add_help=False)
    parent.add_argument('--verbose', '-v', action='count', default=0,
                        help='increase level of verbosity (repeat up to 3 times)')
    # parent.add_argument('--image-root', '-i', type=dir_type, required=True,
    #                     help='root folder for new images files')

    subparsers = parser.add_subparsers(help='command help',
                                       title='valid sub commands')

    # ub command: to-web
    to_web = subparsers.add_parser('to-web',
                                   parents=[parent], 
                                   help='convert contents of slides/ to web/')

    to_web.set_defaults(func=convert_to_web_cmd)

    # sub command: convert to reveal.js
    to_reveal = subparsers.add_parser('to-reveal', 
                                      parents=[parent], 
                                      help='Convert to reveal.js slidedeck.')
    to_reveal.add_argument('source', type=argparse.FileType('r'))
    to_reveal.set_defaults(func=convert_to_reveal_cmd)
    
    return parser

def main():
    parser = get_parser()

    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()
