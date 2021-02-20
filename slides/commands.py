

def add_parser_convert(subparsers):
    sp = subparsers.add_parser('convert',
                               help="Convert slides to reveal.js")
    sp.add_argument('source', help='Source presentation.')
    sp.add_argument('target', help='Target file (for reveal.js and deckset) or folder (for wordpress).')
    sp.add_argument('template', help='The template to use')
    sp.set_defaults(func=cmd_convert_slides)


# TODO: maybe port this command, move argument parser to code
def add_parser_skeleton(subparsers):
    sp = subparsers.add_parser('skeleton',
                               help="Create skeleton directories and files for slides.")
    sp.add_argument('config', help='yaml file with presentation structure')
    sp.add_argument('target', help='Target directory for skeleton files.')
    sp.set_defaults(func=cmd_create_source_files_for_slides)

