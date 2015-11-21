__author__ = 'Davide'

import pathlib
import shutil
import sys
import argparse
import logging


def parseArgs():
    parser = argparse.ArgumentParser(description='Apply diffs.')
    parser.add_argument('diff_file', type=str, help='diff file')
    parser.add_argument('path_from', type=str, help='src folder')
    parser.add_argument('path_to', type=str, help='dst folder')
    res = parser.parse_args(sys.argv[1:])
    return res


def add(line, path_from, path_to):
    fname = line.split(" ", 1)[1]
    path_from /= fname
    path_to /= fname
    if path_from.is_dir():
        path_to.mkdir()
        logging.log(logging.INFO, "Created directory {}".format(path_to))
    elif path_from.is_file():
        shutil.copy2(str(path_from), str(path_to))
        logging.log(logging.INFO, "Copied file from {} to {}".format(path_from, path_to))


def remove(line, path_from, path_to):
    path_to = path_to / line.split(" ", 1)[1]
    if path_to.is_dir():
        path_to.rmdir()
        logging.log(logging.INFO, "Deleted directory {}".format(path_to))
    elif path_to.is_file():
        path_to.unlink()
        logging.log(logging.INFO, "Deleted file {}".format(path_to))


def update(line, path_from, path_to):
    fname = " ".join(line.split(" ")[1:-1])
    path_from /= fname
    path_to /= fname
    if path_from.is_file():
        shutil.copy2(str(path_from), str(path_to))
        logging.info("Copied file from {} to {}".format(path_from, path_to))


def dir2file(line, path_from, path_to):
    fname = line.split(" ", 1)[1]
    path_from /= fname
    path_to /= fname
    if path_to.is_dir():
        path_to.rmdir()
    shutil.copy2(str(path_from), str(path_to))
    logging.info("Copied file from {} to {}".format(path_from, path_to))


def file2dir(line, path_from, path_to):
    fname = line.split(" ", 1)[1]
    path_from /= fname
    path_to /= fname
    if path_to.is_file():
        path_to.unlink()
    path_to.mkdir()
    logging.info("Created directory {}".format(path_to))

def apply_diffs(diff_file, path_from, path_to):
    with diff_file.open() as f:
        for line in f:
            try:
                line = line.strip()
                if line.startswith("+"):
                    add(line, path_from, path_to)
                elif line.startswith("-"):
                    remove(line, path_from, path_to)
                elif line.startswith("*"):
                    update(line, path_from, path_to)
                elif line.startswith("d"):
                    dir2file(line, path_from, path_to)
                elif line.startswith("f"):
                    file2dir(line, path_from, path_to)
            except PermissionError:
                pass


def main():
    logging.basicConfig(level=logging.INFO)
    args = parseArgs()
    path_from = pathlib.Path(args.path_from).resolve()
    path_to = pathlib.Path(args.path_to).resolve()
    diff_file = pathlib.Path(args.diff_file).resolve()
    apply_diffs(diff_file, path_from, path_to)


if __name__ == "__main__":
    main()
