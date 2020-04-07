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
# Opener which will be used for remote calls
OPENER = gladweb.cache.CachingOpener(CACHE)
# Metadata object to store specification metadata
METADATA = gladweb.metadata.Metadata(CACHE, OPENER)

# Path to a folder which will be used to store generation results
TEMP = os.path.join(base_path, 'temp')

# Generate static html files for /generated
# the webserver needs to be configured to serve /generated instead of passing
# requests through to glad-web.
# Note: /generated/icons still needs to be served by glad-web
FREEZE = True

# Automatic cron/cleanup timer in seconds, defaults to 23 hours.
# Disable cron by setting it to 0.
CRON = 23 * 60 * 60


try:
    from local_config import *
except ImportError:
    pass
