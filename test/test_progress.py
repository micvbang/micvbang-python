import os
import io

import micvbang as mvb


class ReusableStringIO(io.StringIO):
    def close(self):
        self.seek(0)


def test_progress_input_equals_output():
    """ Verify that values from original iterator are returned.
    """
    dummy_f = ReusableStringIO()
    lst = list(range(1000))

    # Using ProgressTracker as iterator
    it = iter(mvb.ProgressTracker(lst, f=dummy_f))
    for expected, got in zip(lst, it):
        assert expected == got

    # Using ProgressTracker.iter_ids
    got_it = mvb.ProgressTracker(lst, f=dummy_f).iter_ids()
    for expected, (_, got) in zip(lst, got_it):
        assert expected == got


def test_iter_progress_resume():
    """ When using iter, verify that progress is automatically tracked and correctly continued.
    """
    progress_f = ReusableStringIO()
    r_len = 1000
    half_len = int(r_len / 2)

    # Empty half of the iterator
    pt_iter = iter(mvb.ProgressTracker(range(r_len), f=progress_f))
    for _ in range(half_len):
        next(pt_iter)
    pt_iter.close()

    # Use progress_f to continue from last processed iteration.
    continue_pt = mvb.ProgressTracker(range(r_len), f=progress_f)
    continue_it = continue_pt.iter()

    for expected in range(half_len, half_len * 2):
        assert expected == next(continue_it)

    assert continue_pt.skips == half_len


def test_iter_ids_must_call_processed():
    """ When using iter_ids, verify that `processed` must be called in order to track progress.
    """
    progress_f = ReusableStringIO()

    def make_iter():
        return iter(range(1000))

    # Run iterator through ProgressTracker, but do not mark iterations as processed.
    stopped_pt = mvb.ProgressTracker(make_iter(), f=progress_f)
    stopped_it = stopped_pt.iter_ids()
    for _ in make_iter():
        next(stopped_it)

    stopped_it.close()
    progress_f.seek(0, os.SEEK_END)
    assert progress_f.tell() == 0

    # ProgressTracker iterator starts from beginning again.
    continue_pt = mvb.ProgressTracker(make_iter(), f=progress_f)
    continue_it = continue_pt.iter_ids()

    for expected in make_iter():
        _, got = next(continue_it)
        assert expected == got

    assert continue_pt.skips == 0
