import os
import gladweb.cache


base_path = os.path.abspath(os.path.split(__file__)[0])
cache_path = os.path.join(base_path, 'cache')


CACHE = gladweb.cache.FileCache(cache_path)
