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
CACHE = gladweb.cache.FileCache(os.path.join(base_path, 'cache'))

# Path to a folder which will be used to store generation results
TEMP = os.path.join(base_path, 'temp')

try:
    from local_config import *
except ImportError:
    pass
