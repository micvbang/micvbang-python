import os
import micvbang as mvb


class ProgressTracker(object):
    """ The return value of get_id must not contain newlines.
    """

    def __init__(self, it, get_id=None, f=None, fpath=None, flush_freq=0, print_skips_freq=0):
        self._it = it
        self._get_id = get_id or (lambda x: str(x))
        self._flush_freq = flush_freq
        self._print_skips_freq = print_skips_freq

        self.skips = 0
        self._ids = set()
        self._closed = False

        self._progress_f = self._make_f(f, fpath)

    def _make_f(self, f, fpath):
        if f is not None:
            return f

        p = fpath
        if p is None:
            p = mvb.here('progress.gz')

        mode = 'a+'
        _, ext = os.path.splitext(p)
        if ext == '.gz':
            mode += 't'

        return mvb.open(p, mode)

    def _print_skips(self):
        if self._print_skips_freq and self.skips % self._print_skips_freq == 0:
            print(" ... skipped {} ...".format(self.skips))

    def _flush(self, num_iter, f):
        if self._flush_freq and (num_iter - self.skips) % self._flush_freq == 0:
            getattr(f, 'flush', lambda: None)()

    def processed(self, id):
        """ Mark an id as processed.

        This means that it will not be returned when creating iterators using the same
        progress file.
        """
        self._ids.add(id)
        self._progress_f.write("{id}\n".format(id=id))

    def __iter__(self):
        return self.iter()

    def iter(self):
        """ Return an iterator that iterates over `it` and yields the values produced by `it`. 
        The progress of `it` is automatically tracked.

        Values returned by `it` will be marked as processed _before_ they are returned to the user.
        Note the potential off-by-one error that will happen if a value yielded by the iterator is
        not actually processed.
        """
        for id, value in self.iter_ids():
            self.processed(id)
            yield value

    def iter_ids(self):
        """ Return an iterator that iterates over `it` and yields an (id, value)-tuple, where id
        is the value computed by get_id(value), and value is the value returned by `it`.

        In order to mark a value as processed, `processed` must be called with `id`.
        """
        self._ids = set(l[:-1] for l in self._progress_f.readlines())
        self._progress_f.seek(0)

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

                self._flush(num_iter, self._progress_f)
