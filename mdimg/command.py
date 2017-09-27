# -*- coding: utf-8 -*-

import argparse
import logging
import os

from image_update import check_images_cmd, update_images_cmd


def dir_type(dirname):
    # type for argparse
    if os.path.isdir(dirname):
        return os.path.normpath(dirname)
    raise argparse.ArgumentTypeError('%s is not a valid directory' % dirname)


def get_parser():
    parser = argparse.ArgumentParser(
        description='update images referenced in source markdown files (.md, .mmd, .txt) to new paths.')

    parent = argparse.ArgumentParser(add_help=False)
    parent.add_argument('-d', '--debug', help="print debug output",
                        action="store_const", dest="loglevel", const=logging.DEBUG,
                        default=logging.WARNING)
    parent.add_argument('-v', '--verbose', help="more detailed output",
                        action="store_const", dest="loglevel", const=logging.INFO)

    parent.add_argument('--image-root', '-i', type=dir_type, required=True,
                        help='root folder for new images files')

    subparsers = parser.add_subparsers(help='command help',
                                       title='valid sub commands')

    # sub command: check-images
    check_images = subparsers.add_parser('duplicates',
                                         parents=[parent],
                                         help='list all image paths and check for ambiguous names')

    check_images.set_defaults(func=check_images_cmd)

    # sub command: run
    update_img = subparsers.add_parser('update',
                                       parents=[parent],
                                       help='update all files, list ambiguous and missing image references.')
    update_img.add_argument('document_root', type=dir_type,
                            help='root folder for documents to update')
    update_img.add_argument('--commit', '-c', action='store_true',
                            help='commit result to file')
    update_img.add_argument('--keep-backup', '-k', action='store_true',
                            help='keep backup of original file')
    update_img.set_defaults(func=update_images_cmd)

    return parser


def main():
    parser = get_parser()
    args = parser.parse_args()
    logging.basicConfig(format='%(message)s', level=args.loglevel)
    args.func(args)
