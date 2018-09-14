import hashlib
import os
import shutil
import werkzeug
from contextlib import closing

from glad.opener import URLOpener
from gladweb.util import remove_file_or_dir

class FileCache(object):
    def __init__(self, path):
        self.path = os.path.abspath(path)

        self._gen_funcs = dict()

    def register(self, name, gen_func):
        self._gen_funcs[name] = gen_func

        with closing(gen_func()) as src:
            with self.open(name, 'wb') as dst:
                # TODO very memory inefficient
                dst.write(src.read())

    def clear(self):
        for name in os.listdir(self.path):
            remove_file_or_dir(os.path.join(self.path, name))

    def remove(self, filename):
        remove_file_or_dir(self.get_path(filename))

    def get_path(self, filename):
        filename = werkzeug.utils.secure_filename(filename)
        return os.path.join(self.path, filename)

    def open(self, filename, mode='rb'):
        return open(self.get_path(filename), mode=mode)

    def exists(self, filename):
        return os.path.exists(self.get_path(filename))


class CachingOpener(URLOpener):
    def __init__(self, cache):
        URLOpener.__init__(self)

        self.cache = cache

    def build_key(self, url, data=None):
        h = hashlib.md5()
        h.update(url.encode('utf-8'))
        if data is not None:
            h.update(data.encode('utf-8'))

        name = url.split('?')[0].split('#')[0].split('/')[-1]
        return name + '_' + h.hexdigest()

    def urlopen(self, url, data=None, *args, **kwargs):
        key = self.build_key(url, data=data)
        if not self.cache.exists(key):
            self.cache.register(key, lambda: URLOpener.urlopen(self, url, data, *args, **kwargs))

        return self.cache.open(key)

    def urlretrieve(self, url, filename, data=None):
        key = self.build_key(url, data=data)
        if not self.cache.exists(key):
            self.cache.register(key, lambda: URLOpener.urlopen(self, url, data))

        url = 'file:' + self.cache.get_path(key)
        return URLOpener.urlretrieve(self, url, filename, data)