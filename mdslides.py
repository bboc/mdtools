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

    # # sub command: run
    # update_img = subparsers.add_parser('update-images', 
    #                             parents=[parent], 
    #                             help='update all files, list ambiguous and missing image references.')
    # update_img.add_argument('document_root',  type=dir_type,
    #                     help='root folder for documents to update')
    # update_img.add_argument('--commit', '-c', action='store_true', 
    #                     help='commit result to file')
    # update_img.add_argument('--keep-backup', '-k', action='store_true', 
    #                     help='keep backup of original file')
    # update_img.set_defaults(func=update_images_cmd)

    # list_broken_images = subparsers.add_parser('list-broken-images', 
    #                      parents=[parent], 
    #                      help='parse all files, print ambiguous and missing image references.')
    # list_broken_images.set_defaults(func=list_broken_images_cmd)

    return parser

def main():
    parser = get_parser()

    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()
