import json
from pprint import pprint


def validate_manifest(manifestfile):
    with open(manifestfile) as fp:
        data = json.load(fp)
    pprint(data)


if __name__ == '__main__':
    import sys
    manifestfile = sys.argv[1]
    validate_manifest(manifestfile)
