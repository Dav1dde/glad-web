import os
import random
import string
import sys
import werkzeug
from glad.parse import Spec

if sys.version_info >= (3, 0):
    from urllib.request import urlretrieve
else:
    from urllib import urlretrieve


KHRPLATFORM_URL = 'https://www.khronos.org/registry/egl/api/KHR/khrplatform.h'


def generate_filename(allowed_chars, extension=''):
    return '{0}.{1}'.format(
        ''.join(random.sample(allowed_chars, random.randint(5, 15))),
        extension
    )


class FileCache(object):
    def __init__(self, path):
        self.path = os.path.abspath(path)

        self._allowed_chars = string.ascii_letters + string.digits

    def get_path(self, filename):
        filename = werkzeug.utils.secure_filename(filename)
        return os.path.join(self.path, filename)

    def open_unique_file(self, mode='rb', extension=''):
        # there might be race conditions, do we care?
        name = generate_filename(self._allowed_chars, extension=extension)
        while self.exists(name):
            name = generate_filename(self._allowed_chars, extension=extension)

        return self.get_path(name), self.open(name, mode=mode)

    def open(self, filename, mode='rb'):
        return open(self.get_path(filename), mode=mode)

    def open_specification(self, name, mode='rb'):
        filename = '{0}.xml'.format(name.lower())
        if not self.exists(filename):
            urlretrieve(Spec.API + filename, self.get_path(filename))

        return self.open(filename, mode=mode)

    def get_khrplatform(self):
        path = self.get_path('khrplatform.h')
        if not self.exists('khrplatform.h'):
            urlretrieve(KHRPLATFORM_URL, path)

        return path

    def exists(self, filename):
        return os.path.exists(self.get_path(filename))
