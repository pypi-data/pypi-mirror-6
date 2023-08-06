import argparse
import os.path

from . import apt
from . import util

def main():
    parser = argparse.ArgumentParser(
        prog='periapt',
        description='Generate an apt repository',
    )

    parser.add_argument(
        'origin',
        help='Brief repository description (e.g., vendor name)',
    )
    parser.add_argument(
        'input',
        help='Path of package tree',
    )
    parser.add_argument(
        'output',
        help='Path where repository will be generated',
    )
    parser.add_argument(
        '-k', '--key',
        help='Specific GPG key ID to use for signing (if not default key)',
    )

    args = parser.parse_args()

    if not util.has_program('dpkg-deb'):
        parser.error(
            'Could not find dpkg-deb in $PATH. Is this a Debian system?'
        )

    if not os.path.isdir(args.input):
        parser.error('Input path %s is not a directory.' % args.input)
    if not os.path.isdir(args.output):
        parser.error('Output path %s is not a directory.' % args.output)

    apt.generate_repository(
        args.origin,
        args.input,
        args.output,
        args.key,
    )

if __name__ == '__main__':
    main()
