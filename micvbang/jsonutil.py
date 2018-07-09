import os
import json

from .io import open_file


def load_json(path):
    mode = 'r'

    _, ext = os.path.splitext(path)
    if ext == '.gz':
        mode += 't'

    with open_file(path, mode) as f:
        return json.load(f)
