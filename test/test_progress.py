import io

import micvbang as mvb


def test_progress_input_equals_output():
    """ Verify that values from original iterator are returned.
    """
    dummy_f = io.StringIO()
    lst = list(range(1000))

    expected_it = lst
    got_it = mvb.ProgressTracker(lst, f=dummy_f).iter()

    for expected, got in zip(expected_it, got_it):
        assert expected == got


def test_progress_resume():
    """ Verify that progress file is used to skip elements with ids that were already seen.
    """
    progress_f = ReusableStringIO()
    r_len = 1000
    half_len = int(r_len / 2)

    stopped_it = mvb.ProgressTracker(range(r_len), f=progress_f).iter()
    for _ in range(half_len):
        next(stopped_it)

    stopped_it.close()

    # Create new range for progress, using progress_f to continue from last point.
    continue_pt = mvb.ProgressTracker(range(r_len), f=progress_f)
    continue_it = continue_pt.iter()

    expected_it = iter(range(half_len, half_len * 2))

    for _ in range(half_len):
        assert next(expected_it) == next(continue_it)

    assert continue_pt.skips == half_len


class ReusableStringIO(io.StringIO):
    def close(self):
        self.seek(0)
