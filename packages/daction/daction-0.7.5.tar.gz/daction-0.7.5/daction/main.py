""" entry point """

import argparse
import sys
import daction
from daction.daction import perform_action


def main():
    parser = argparse.ArgumentParser(description='Performs custom action to all/specified elements in a directory.')
    parser.add_argument('path', nargs='?', help='Path to a directory in which you want to do some action. For example: "/foo/bar" or "/foo/*bar*"')
    parser.add_argument('--action', nargs='?', default='ls -l', help='Action to perform. For example: "ls -la"')
    parser.add_argument('--version', action='store_true', help="Print the version number and exit.")
    args = parser.parse_args()

    if args.version:
        print(daction.version)
        return
    if not args.path:
        print('You must supply a path\n', file=sys.stderr)
        parser.print_help()
        return

    perform_action(args.path, args.action)