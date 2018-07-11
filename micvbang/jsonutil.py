import os
import json

import micvbang as mvb


def json_load(path, none_on_error=False):
    mode = 'r'

    _, ext = os.path.splitext(path)
    if ext == '.gz':
        mode += 't'

    with mvb.open(path, mode) as f:
        try:
            return json.load(f)
        except json.JSONDecodeError as e:
            if none_on_error:
                return None
            raise e


def json_dump(obj, path):
    mode = 'w'

    _, ext = os.path.splitext(path)
    if ext == '.gz':
        mode += 't'

    with mvb.open(path, mode) as f:
        return json.dump(obj, f)
