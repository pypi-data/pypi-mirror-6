# -*- coding: utf-8 -*-
#:Progetto:  metapensiero.extjs.desktop
#:Creato:    mer 28 nov 2012 16:28:06 CET
#:Autore:    Lele Gaifax <lele@metapensiero.it>
#:Licenza:   GNU General Public License version 3 or later
#

import sys

from versio.version import Version
from versio.version_scheme import (
    Pep440VersionScheme,
    Simple3VersionScheme,
    Simple4VersionScheme,
    VersionScheme,
    )

Simple2VersionScheme = VersionScheme(name="A.B",
                                     parse_regex=r"^(\d+)\.(\d+)$",
                                     clear_value='0',
                                     format_str="{0}.{1}",
                                     fields=['Major', 'Minor'],
                                     description='Simple Major.Minor version scheme')

schemesmap = {
    'pep440': Pep440VersionScheme,
    'simple2': Simple2VersionScheme,
    'simple3': Simple3VersionScheme,
    'simple4': Simple4VersionScheme
}

allfields = sorted(set(Pep440VersionScheme.fields) |
                   set(Simple2VersionScheme.fields) |
                   set(Simple3VersionScheme.fields) |
                   set(Simple4VersionScheme.fields))


def read_version(f, scheme):
    try:
        version = open(f).read().strip()
        return Version(version, scheme=scheme)
    except:
        print("ERROR: cannot parse '%s' with scheme %s" % (version,
                                                           scheme.name))
        sys.exit(128)


def main():
    import argparse
    from os.path import dirname, join
    from textwrap import indent

    version_txt = join(dirname(dirname(dirname(__file__))), 'version.txt')

    parser = argparse.ArgumentParser(
        description="Version bumper.",
        epilog='\n\n'.join('%s:\n%s' % (
            scheme, indent(schemesmap[scheme].description, '  '))
                           for scheme in ['pep440', 'simple2',
                                          'simple3', 'simple4']),
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('file', default=version_txt, nargs='?',
                        help="The file containing the version number"
                        " (defaults to %s)" % version_txt)
    parser.add_argument('--scheme', default='simple2',
                        choices=['pep440', 'simple2', 'simple3', 'simple4'],
                        help="Scheme to follow, by default 'simple2'")
    parser.add_argument('--field', choices=allfields, default='minor',
                        help="Which field to bump, by default the minor number")
    parser.add_argument('--index', default=-1, type=int,
                        help="For scheme pep440, the part of the release number"
                        " to bump")
    parser.add_argument('--dry-run', default=False, action="store_true",
                        help="Do not rewrite the file, just print the new version")
    args = parser.parse_args()

    scheme = schemesmap[args.scheme]
    if not args.field in scheme.fields:
        print("ERROR: field '%s' not recognized by scheme %s"
              " (hint: choose one between %s)" % (args.field,
                                                  scheme.name,
                                                  scheme.fields))
        sys.exit(128)

    version = read_version(args.file, scheme)

    if args.dry_run:
        print("Old version: %s" % version)

    version.bump(args.field, args.index)

    if args.dry_run:
        print("New version: %s" % version)
    else:
        with open(args.file, 'w') as s:
            s.write(str(version))

if __name__ == '__main__':
    main()
