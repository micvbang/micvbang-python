from .io import open_file


class ProgressTracker(object):
    def __init__(self, it, get_id, fpath=None, flush_freq=0, print_skips_freq=0):
        self.skips = 0
        self._get_id = get_id
        self._it = it

        self._ids = set()

        self._flush_freq = flush_freq
        self._print_skips_freq = print_skips_freq

        self._fpath = fpath
        if fpath is None:
            self._fpath = 'progress.gz'

        try:
            with open_file(self._fpath, 'rt') as f:
                self._ids = set(f.read().split('\n'))
        except FileNotFoundError:
            pass

    def iter(self):
        with open_file(self._fpath, 'at') as f:
            for i, data in enumerate(self._it):
                id = self._get_id(data)
                if id in self._ids:
                    self.skips += 1
                    if self._print_skips_freq and self.skips % self._print_skips_freq == 0:
                        print(" ... skipped {} ...".format(self.skips))
                    continue

                yield data
                self._ids.add(id)
                f.write("{}\n".format(id))

                if self._flush_freq and i % self._flush_freq == 0:
                    f.flush()
