# ---
# Default Configuration
# ---

import os
import string

# ---
# Flask
# ---
# This key MUST be changed before you make a site public, as it is used
# to sign the secure cookies used for sessions.
SECRET_KEY = 'ChangeMeOrGetHacked'


try:
    from local_config import *
except ImportError:
    pass