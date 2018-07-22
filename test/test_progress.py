import os
import io
from collections import namedtuple

import micvbang as mvb
from micvbang.progress import ReadAppendFile


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
    """ When using iter, verify that progress is automatically tracked and correctly continued
    on a clean exit.
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


def test_iter_progress_resume_on_exception():
    """ When using iter, verify that progress is automatically tracked and correctly continued
    on an unclean exit.
    """
    progress_f = ReusableStringIO()
    r_len = 1000
    half_len = int(r_len / 2)

    pt = mvb.ProgressTracker(range(r_len), f=progress_f)
    pt_iter = iter(pt.iter_ids())

    try:
        for i, (id, _) in enumerate(pt_iter):
            # HACK: utilizing knowledge that ProgressTracker will call _get_id to force
            # an unclean exit of the iterator.
            if i == half_len:
                pt._get_id = None
                continue

            pt.processed(id)
    except TypeError:
        pass

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


def test_make_file_obj_success():
    """ Verify that different types of progress files are supported.

        - No progress file given
        - path names, including automatic gzipping .gz files
        - file handle to read- and appendable file
        - ReadAppendFile objects
    """

    TestFile = namedtuple('TestFile', ['name', 'make'])

    def make_test_files():
        # None, use default progress file
        yield TestFile(name=mvb.here(mvb.ProgressTracker.DEFAULT_F_NAME), make=lambda: None)

        # path names
        fname = mvb.random_file_name('.txt')
        yield TestFile(name=fname, make=lambda: fname)

        fname = mvb.random_file_name('.gz')
        yield TestFile(name=fname, make=lambda: fname)

        # read and appendable file
        fname = mvb.random_file_name('.txt')
        yield TestFile(name=fname, make=lambda: mvb.open(fname, 'a+'))

        # ReadAppendFile
        fname = mvb.random_file_name('.txt')
        yield TestFile(name=fname, make=lambda: ReadAppendFile(
            open_read=lambda: mvb.open(fname, 'r'),
            open_append=lambda: mvb.open(fname, 'a')
        ))

        fname = mvb.random_file_name('.gz')
        yield TestFile(name=fname, make=lambda: ReadAppendFile(
            open_read=lambda: mvb.open(fname, 'rt'),
            open_append=lambda: mvb.open(fname, 'at')
        ))

    r = list(range(500))
    expected_skips = len(r)

    # Verify that progress file is created and can be continued from.
    for test_file in make_test_files():
        for _ in mvb.ProgressTracker(r, f=test_file.make()):
            pass

        pt = mvb.ProgressTracker(r, f=test_file.make())
        for _ in pt:
            pass

        assert expected_skips == pt.skips
        assert os.path.exists(test_file.name)
        os.remove(test_file.name)


def test_tracker_can_close():
    """ Verify that no more iterations are performed once ProgressTracker.close has been called.
    """
    r = range(500)
    half_len = len(r) / 2
    pt = mvb.ProgressTracker(r, f=ReusableStringIO())

    i = 0
    for i, _ in enumerate(pt):
        if i == half_len:
            pt.close()

        if i > half_len:
            assert False

    assert i == half_len


def test_tracker_close_before_iterator():
    """ Verify that no iterations are performed when ProgressTracker.close is called before
    creating an iterator from the ProgressTracker.
    """
    r = range(500)
    pt = mvb.ProgressTracker(r, f=ReusableStringIO())
    pt.close()

    i = 0
    for i, _ in enumerate(pt):
        assert False

    assert 0 == i
