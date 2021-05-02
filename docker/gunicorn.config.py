import os.path

base_path = os.path.split(os.path.abspath(__file__))[0]

bind = '0.0.0.0:8080'
workers = 5
worker_class = 'eventlet'
keepalive = 5
loglevel = 'warning'
proc_name = 'glad-web'

