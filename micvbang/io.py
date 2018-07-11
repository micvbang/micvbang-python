import os
import sys
import gzip
import stat


def here(*ps):
    """ Return script execution path os.path.join'ed with the given arguments.
    """
    return os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), *ps)


def _list_dir(path, dirs, files, ext):
    for fname in os.listdir(path):
        fpath = os.path.join(path, fname)
        mode = os.stat(fpath).st_mode

        isdir = stat.S_ISDIR(mode)
        isfile = stat.S_ISREG(mode)

        d = dirs and isdir
        f = files and isfile and (ext is None or os.path.splitext(fname)[1] == ext)

        if d or f:
            yield fpath


def list_dir(path='.', dirs=False, files=True, ext=None, recursive=False):
    """ List the contents of a directory.
    If recursive is set to True, list_dir will recurse through sub-dirs as
    well.

    Returns directories if dirs is set to True.
    Returns files if files is set True.
    Returns only files with the given extension if ext is set. Note that
        the extension includes the dot, i.e. '.jpg'.
    """
    if not recursive:
        yield from _list_dir(path, dirs, files, ext)
        return

    yield from _list_dir(path, dirs=False, files=True, ext=ext)

    for d in _list_dir(path, dirs=True, files=False, ext=None):
        if dirs:
            yield d
        yield from list_dir(d, dirs, files, ext, recursive=True)


_open = open


def open(path, mode='r'):
    """ Open a file and return a stream.

    If the file has .gz extension, `gzip.open` is used in place of `open`.
    """
    _, ext = os.path.splitext(path)
    if ext == '.gz':
        return gzip.open(path, mode)

    return _open(path, mode)


def open_file(path, mode='r'):
    return open(path, mode)
