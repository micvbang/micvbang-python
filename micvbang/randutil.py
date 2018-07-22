import random
import string


def random_file_name(ext):
    return '{name}{ext}'.format(name=random_string(), ext=ext)


def random_string(length=25):
    return ''.join(random.choice(string.ascii_letters) for _ in range(length))
