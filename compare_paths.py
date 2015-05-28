__author__ = 'Davide'

import argparse
import pathlib
import zlib
import sys
from enum import Enum


class Res:
    def __init__(self, added=None, removed=None, modified=None,
                 dir2file=None, file2dir=None):
        self.added = added or set()
        self.removed = removed or set()
        self.modified = modified or set()
        self.dir2file = dir2file or set()
        self.file2dir = file2dir or set()

    def update(self, r):
        self.added |= r.added
        self.removed |= r.removed
        self.modified |= r.modified
        self.dir2file |= r.dir2file
        self.file2dir |= r.file2dir


class ModReason(Enum):
    SAME = 0
    DIFF_SIZE = 1
    DIFF_CRC = 2

    def __str__(self):
        return self.name


def compute_crc32(fp):
    h = 0
    while True:
        data = fp.read(8192)
        if not data:
            break
        h = zlib.crc32(data, h)
    return h


def equals_files(p1_d, p2_d, use_modification_date):
    stat1 = p1_d.stat()
    stat2 = p2_d.stat()

    if stat1.st_size != stat2.st_size:
        return False, ModReason.DIFF_SIZE

    if use_modification_date and stat1.st_mtime == stat2.st_mtime:
        return True, ModReason.SAME

    with p1_d.open("rb") as f1:
        h1 = compute_crc32(f1)
    with p2_d.open("rb") as f2:
        h2 = compute_crc32(f2)
    if h1 == h2:
        return True, ModReason.SAME
    else:
        return False, ModReason.DIFF_CRC


def search(p1, p2, use_modification_date, verbose=False):
    if verbose:
        print("Matching", p1, "with", p2)
    c1 = set(d.relative_to(p1) for d in p1.iterdir())
    c2 = set(d.relative_to(p2) for d in p2.iterdir())

    cur_res = Res(added={p2 / d for d in c2 - c1},
                  removed={p1 / d for d in c1 - c2})

    for d in (c1 & c2):
        p1_d = p1 / d
        p2_d = p2 / d

        if p1_d.is_dir() and p2_d.is_dir():
            res = search(p1_d, p2_d, use_modification_date, verbose)
            cur_res.update(res)

        elif p1_d.is_file() and p2_d.is_file():
            b, reason = equals_files(p1_d, p2_d, use_modification_date)
            if not b:
                cur_res.modified.add((p1_d, reason))

        else:
            if p1_d.is_file() and p2_d.is_dir():
                cur_res.file2dir.add(p1_d)
            else:
                cur_res.dir2file.add(p1_d)

    return cur_res

def parseArgs():
    parser = argparse.ArgumentParser(description='Folder comparer.')
    parser.add_argument('path_from', type=str, help='src folder')
    parser.add_argument('path_to', type=str, help='dst folder')
    parser.add_argument('-m', '--modified', dest='use_date',
                        action='store_const', default=False, const=True,
                        help='use the modification date')
    res = parser.parse_args(sys.argv[1:])
    return res

def main():
    args = parseArgs()
    res = search(pathlib.Path(args.path_from).resolve(),
                 pathlib.Path(args.path_to).resolve(),
                 use_modification_date=args.use_date)
    for x in sorted(res.added):
        print("+", x)
    for x in sorted(res.removed):
        print("-", x)
    for x in sorted(res.modified):
        print("*", x[0], "[{}]".format(x[1]))
    for x in sorted(res.dir2file):
        print("d", x)
    for x in sorted(res.file2dir):
        print("f", x)


if __name__ == "__main__":
    main()
