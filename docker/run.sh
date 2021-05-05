#!/bin/bash

if [[ -n "$SERVER_NAME" ]]; then
    echo "SERVER_NAME = '$SERVER_NAME'" > local_config.py
fi

if [[ -n "$GLAD_LATEST" ]]; then
  pip install --upgrade git+https://github.com/dav1dde/glad.git#egg=glad
fi

python -m gladweb init

exec gunicorn -c gunicorn.config.py 'gladweb:create_application(debug=False, verbose=None)' "$@"

