# ---
# Default Configuration
# ---

import os

import gladweb.cache

base_path = os.path.abspath(os.path.join(os.path.split(__file__)[0], '..'))


# ---
# Flask
# ---
# This key MUST be changed before you make a site public, as it is used
# to sign the secure cookies used for sessions.
SECRET_KEY = 'ChangeMeOrGetHacked'


# ---
# Glad Web
# ---
# A cache, which will be used to store/retrieve various files.
cache_path = os.path.join(base_path, 'cache')
if not os.path.exists(cache_path):
    os.makedirs(cache_path)
CACHE = gladweb.cache.FileCache(cache_path)

# Path to a folder which will be used to store generation results
TEMP = os.path.join(base_path, 'temp')

# Generate static html files for /generated
# the webserver needs to be configured to serve /generated instead of passing
# requests through to glad-web.
# Note: /generated/icons still needs to be served by glad-web
FREEZE = True

try:
    from local_config import *
except ImportError:
    pass
