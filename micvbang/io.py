import os
import sys
import gzip


def here(*ps):
    """ Return script execution path os.path.join'ed with the given arguments.
    """
    return os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), *ps)


def list_dir(path, dirs=False, files=True, ext=None):
    """ List the contents of a directory.

    Returns directories if dirs is set.
    Returns files if files is set.
    Returns only files with the given extension if ext is set.
    """
    for fname in os.listdir(path):
        d = dirs and os.path.isdir(fname)
        f = files and os.path.isfile(fname)
        e = ext is None or os.path.splitext(fname)[1] == ext
        if d or f or e:
            yield os.path.join(path, fname)


def open_file(path, mode='r'):
    """ Open a file and return a stream.

    If the file has .gz extension, `gzip.open` is used in place of `open`.
    """
    _, ext = os.path.splitext(path)
    if ext == '.gz':
        return gzip.open(path, mode)
    else:
        return open(path, mode)
