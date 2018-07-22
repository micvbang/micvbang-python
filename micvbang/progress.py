import os
from collections import namedtuple

import micvbang as mvb


ReadAppendFile = namedtuple('ReadAppendFile', ['open_read', 'open_append'])


class ProgressTracker(object):
    """ Track and continue progress over iterators, saving state in a file-like object.

    """

    DEFAULT_F_NAME = 'progress.gz'

    def __init__(self, it, get_id=None, f=None, flush_freq=0, print_skips_freq=0):
        """
        Arguments:
            it(iterable): Iterable used to to make the iterator to track the progress of.
            get_id(function): Function mapping values generated from :param it: to unique ids of type string.


        .. note::

            :param get_id: must return a string value that does **not** contain newlines.
        """
        self._it = it
        self._get_id = get_id or (lambda x: str(x))
        self._flush_freq = flush_freq
        self._print_skips_freq = print_skips_freq

        self._made_f = self._make_f(f)
        self._progress_f = None

        self.skips = 0
        self._ids = set()
        self._closed = False

        self._f = f

    def _make_f(self, f_in):
        f = None

        if f_in is None:
            f_in = mvb.here(self.DEFAULT_F_NAME)

        if self._is_file_like(f_in):
            f = f_in
        elif type(f_in) is ReadAppendFile:
            f = f_in
        elif type(f_in) is str:
            _, ext = os.path.splitext(f_in)
            if ext == '.gz':
                f = ReadAppendFile(
                    open_read=lambda: mvb.open(f_in, mode='rt'),
                    open_append=lambda: mvb.open(f_in, mode='at')
                )
            else:
                f = mvb.open(f_in, 'a+')

        return f

    def _is_file_like(self, f):
        return all(getattr(f, attr, False) for attr in ['read', 'write', 'seek'])

    def _print_skips(self):
        if self._print_skips_freq and self.skips % self._print_skips_freq == 0:
            print(" ... skipped {} ...".format(self.skips))

    def _flush(self, num_iter):
        if self._flush_freq and (num_iter - self.skips) % self._flush_freq == 0:
            getattr(self._progress_f, 'flush', lambda: None)()

    def processed(self, id):
        """ Mark an id as processed.

        This means that values with the given id will **not** be returned when creating
        iterators using the same progress file.
        """
        if id not in self._ids:
            self._ids.add(id)
            self._progress_f.write("{id}\n".format(id=id))

    def close(self):
        """ Close :class:`ProgressTracker`. This ensures that no iterators created from the
        instance will progress any further.
        """
        self._closed = True

    def __iter__(self):
        return self.iter()

    def iter(self):
        """ Return an iterator that iterates over the given input iterator and
        automatically tracks its progress. :func:`processed` will
        be called **before** each value is returned to the user.

        .. note::

            Potential off-by-one error here; all ids are marked as `processed`
            **before** they are returned and will therefore never be returned again.
            If the program crashes and the id was not in fact processed by user code,
            it will go unprocessed.
        """
        for id, value in self.iter_ids():
            self.processed(id)
            yield value

    def _read_ids(self, f):
        readlines = getattr(f, 'readlines', False)
        if readlines:
            return set(l[:-1] for l in readlines())

        return set(f.read().split('\n'))

    def _init_ids(self, f):
        if type(f) is ReadAppendFile:
            try:
                with self._made_f.open_read() as f:
                    return self._read_ids(f)
            except FileNotFoundError:
                return set()

        f.seek(0)
        return self._read_ids(f)

    def iter_ids(self):
        """ Return an iterator that yields an (id, data)-tuple. In order to mark an
        iteration as processed, :func:`processed` must be called with the given id.
        """
        self._ids = self._init_ids(self._made_f)

        progress_f = self._made_f
        if type(progress_f) is ReadAppendFile:
            progress_f = self._made_f.open_append()
        self._progress_f = progress_f

        if self._closed:
            return

        with self._progress_f:
            for num_iter, value in enumerate(self._it):
                if self._closed:
                    return

                id = self._get_id(value)
                if id in self._ids:
                    self.skips += 1
                    self._print_skips()
                    continue

                yield id, value

                self._flush(num_iter)
