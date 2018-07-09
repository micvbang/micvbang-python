import os
import sys


def here(*ps):
    return os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), *ps)


def list_dir(path, dirs=False, files=True, ext='*'):
    for fname in os.listdir(path):
        d = dirs and os.path.isdir(fname)
        f = files and os.path.isfile(fname)
        e = ext == '*' or os.path.splitext(fname)[1] == ext
        if d or f or e:
            yield os.path.join(path, fname)
