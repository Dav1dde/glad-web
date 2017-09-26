import os
import random
import shutil
import string
from contextlib import closing

import werkzeug

from glad.opener import URLOpener

try:
    from glad.spec import SPECIFICATIONS
except ImportError:
    from glad.spec import SPECS as SPECIFICATIONS


KHRPLATFORM_URL = 'https://raw.githubusercontent.com/KhronosGroup/EGL-Registry/master/api/KHR/khrplatform.h'


def generate_filename(allowed_chars, extension=''):
    return '{0}.{1}'.format(
        ''.join(random.sample(allowed_chars, random.randint(5, 15))),
        extension
    )


class FileCache(object):
    SPECIFICATIONS = ('egl', 'gl', 'glx', 'wgl')

    def __init__(self, path, opener=None):
        self.path = os.path.abspath(path)
        self.opener = opener
        if self.opener is None:
            self.opener = URLOpener.default()

        self._allowed_chars = string.ascii_letters + string.digits

    def clear(self):
        for name in os.listdir(self.path):
            self.remove(name)

    def remove(self, filename):
        path = self.get_path(filename)
        if os.path.isfile(path) or os.path.islink(path):
            os.remove(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)

    def refresh(self):
        for name in self.SPECIFICATIONS:
            base_url = SPECIFICATIONS[name].API
            filename = '{0}.xml'.format(name.lower())
            # we download, if this fails it is fine, if it succeeds we overwrite
            with closing(self.opener.urlopen(base_url + filename)) as src:
                data = src.read()
                with self.open(filename, 'w') as dst:
                    dst.write(data)

        with closing(self.opener.urlopen(KHRPLATFORM_URL)) as src:
            data = src.read()
            with self.open('khrplatform.h', 'w') as dst:
                dst.write(data)

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
        name = name.lower()
        if name not in self.SPECIFICATIONS:
            raise ValueError('Invalid specification name "{0}".'.format(name))
        filename = '{0}.xml'.format(name.lower())
        if not self.exists(filename):
            Specification = SPECIFICATIONS[name]
            url = Specification.API + Specification.NAME + '.xml'
            self.opener.urlretrieve(url, self.get_path(filename))

        return self.open(filename, mode=mode)

    def get_khrplatform(self):
        path = self.get_path('khrplatform.h')
        if not self.exists('khrplatform.h'):
            self.opener.urlretrieve(KHRPLATFORM_URL, path)

        return path

    def exists(self, filename):
        return os.path.exists(self.get_path(filename))
