Glad-Web
========

This is a webservice for [glad](https://github.com/Dav1dde/glad), a multi-language
GL/GLES/EGL/GLX/WGL loader-generator based on the official specifications.

Official instance running at: http://glad.dav1d.de/


### Requirements: ###

    glad
    gunicorn
    eventlet
    flask
    Flask-AutoIndex

### Cronjob: ###

To delete all temporary files, I recommend running a cronjob every 24 hours:

```sh
#!/bin/sh

cd /home/pyweb/gladweb/glad-web/
source ../bin/activate

exec python -m gladweb cron --age 23
```
### Gunicorn: ###

Start script:

```sh
#!/bin/sh

cd /path/to/gladweb/glad-web/
# assume virtualenv location, might need to be changed
source ../bin/activate

exec gunicorn -c gunicorn.config.py 'gladweb:create_application(debug=False, verbose=None)' "$@"
```

Config:

```python
import os.path

base_path = os.path.split(os.path.abspath(__file__))[0]

bind = '127.0.0.1:5000'
workers = 5
worker_class = 'eventlet'
keepalive = 5
user = 'glad'
errorlog = os.path.join(base_path, 'error.log')
loglevel = 'warning'
proc_name = 'glad gunicorn'
```


### Supervisor: ###

```ini
[program:glad]
command = /path/to/gladweb/glad-web/start_gladweb.sh
directory = /path/to/gladweb/glad-web
user = glad
autostart = True
autorestart = True
stdout_logfile = /var/log/supervisor/glad.log
stderr_logfile = /var/log/supervisor/glad_err.log
```


### Nginx: ###

```nginx
server {
    listen 80;
    server_name localhost;

    root /path/to/glad-web/;

    location / {
        try_files $uri @proxy_to_app;
    }

    location /static {
        alias /path/to/glad-web/gladweb/static;
    }

    # 'frozen' html files
    location /generated {
        default_type text/plain;
        alias /path/to/glad-web/temp;
    }

    # served by flask-silk
    location /generated/icons {
        try_files $uri @proxy_to_app;
    }

    location @proxy_to_app {
        proxy_set_header Host $http_host;
        proxy_set_header X-Forwarded-For  $proxy_add_x_forwarded_for;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_redirect off;

        proxy_pass http://localhost:5000;
    }
}
```
