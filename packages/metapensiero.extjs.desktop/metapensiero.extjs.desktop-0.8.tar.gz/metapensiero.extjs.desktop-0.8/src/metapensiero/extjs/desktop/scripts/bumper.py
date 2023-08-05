# -*- coding: utf-8 -*-
#:Progetto:  metapensiero.extjs.desktop
#:Creato:    mer 28 nov 2012 16:28:06 CET
#:Autore:    Lele Gaifax <lele@metapensiero.it>
#:Licenza:   GNU General Public License version 3 or later
#

def read_version(f):
    try:
        version = open(f).read().strip().split('.')[:2]
        return int(version[0]), int(version[1])
    except:
        return (0, 0)


def write_version(f, version):
    with open(f, 'w') as s:
        s.write('%d.%d' % version)


def bump_version(old_version, part):
    """Increment the version number of a project.

    :param old_version: the previous version
    :param part: a string, either ``major`` or ``minor``
    """

    major, minor = old_version
    if part == 'major':
        major += 1
        minor = 0
    elif part == 'minor':
        minor += 1

    return major, minor


def main():
    import argparse
    from os.path import dirname, join

    version_txt = join(dirname(dirname(dirname(__file__))), 'version.txt')

    parser = argparse.ArgumentParser(description="Version bumper.")

    parser.add_argument('file', default=version_txt, nargs='?',
                        help="The file containing the version number"
                        " (defaults to %s)" % version_txt)
    parser.add_argument('--major', default=False, action="store_true",
                        help="Bump the major number, by default the minor number")
    parser.add_argument('--dry-run', default=False, action="store_true",
                        help="Do not rewrite the file, just print the new version")
    args = parser.parse_args()

    old_version = read_version(args.file)
    new_version = bump_version(old_version, 'major' if args.major else 'minor')

    if args.dry_run:
        print("New version: %d.%d" % new_version)
    else:
        write_version(args.file, new_version)



if __name__ == '__main__':
    main()
