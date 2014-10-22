import sys

from bakery_cli.scripts import genmetadata


def main(argv=None):
    if argv is None:
        argv = sys.argv
    if len(argv) != 2:
        genmetadata.usage()
        return 1
    genmetadata.run(argv[1])
    return 0

if __name__ == '__main__':
    sys.exit(main())
