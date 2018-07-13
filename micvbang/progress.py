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

    def iter(self):
        try:
            self._ids = set(l[:-1] for l in self._progress_f.readlines())
            self._progress_f.seek(0)
        except FileNotFoundError:
            pass

        with self._progress_f:
            for num_iter, data in enumerate(self._it):
                if self._closed:
                    return

                id = self._get_id(data)
                if id in self._ids:
                    self.skips += 1
                    self._print_skips()
                    continue

                self._ids.add(id)
                self._progress_f.write("{id}\n".format(id=id))
                yield data

                self._flush(num_iter, self._progress_f)
