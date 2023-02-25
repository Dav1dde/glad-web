#!/bin/bash

if [[ -n "${SERVER_NAME}" ]]; then
    echo "SERVER_NAME = '$SERVER_NAME'" >> local_config.py
fi

if [[ -n "${SENTRY_DSN}" ]]; then
    echo "SENTRY_CONFIG = {'dsn': '${SENTRY_DSN}'}" >> local_config.py
fi

if [[ -n "${GLAD_LATEST}" ]]; then
    pip install --upgrade --force-reinstall https://github.com/dav1dde/glad/archive/glad2.zip
fi

python -m gladweb init

exec gunicorn -c gunicorn.config.py 'gladweb:create_application(debug=False, verbose=None)' "$@"
