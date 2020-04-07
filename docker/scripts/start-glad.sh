#!/bin/bash

cd /usr/src/app

echo "TEMP = '/glad/tmp'" >> local_config.py

if [[ -n "${SERVER_NAME}" ]]; then
    echo "SERVER_NAME = '$SERVER_NAME'" >> local_config.py
fi

if [[ -n "${SENTRY_DSN}" ]]; then
    echo "SENTRY_CONFIG = {'dsn': '${SENTRY_DSN}'}" >> local_config.py
fi

ln -s /glad/cache ./cache

python -m gladweb init

exec gunicorn -c /glad/conf/gunicorn.config.py 'gladweb:create_application(debug=False, verbose=None)' "$@"


