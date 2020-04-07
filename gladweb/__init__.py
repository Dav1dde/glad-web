import json
import logging
import os
import shutil
import sys
import threading
import time

import werkzeug
from flask import Flask, g
from flask_autoindex import AutoIndexBlueprint

import glad
import gladweb.util
from gladweb.freezer import Freezer
from gladweb.metadata import Metadata

try:
    from raven.contrib.flask import Sentry
    sentry = Sentry()
except ImportError:
    sentry = None


logger = logging.getLogger('gladweb')


class LevelFilter(logging.Filter):
    def __init__(self, levels):
        logging.Filter.__init__(self)
        self.levels = levels

    def filter(self, rec):
        return rec.levelno in self.levels


def setup_logging():
    root_logger = logging.getLogger()
    root_logger.handlers = []

    fmtr = logging.Formatter(
        '[%(asctime)s] %(levelname)s:\t%(message)s', '%m/%d/%Y %H:%M:%S'
    )

    stdout = logging.StreamHandler(sys.stdout)
    low_filter = LevelFilter((logging.DEBUG, logging.INFO))
    stdout.addFilter(low_filter)
    stdout.setFormatter(fmtr)
    root_logger.addHandler(stdout)

    stderr = logging.StreamHandler(sys.stderr)
    high_filter = LevelFilter(
        (logging.WARNING, logging.ERROR, logging.CRITICAL)
    )
    stderr.addFilter(high_filter)
    stderr.setFormatter(fmtr)
    root_logger.addHandler(stderr)

    root_logger.setLevel(logging.INFO)


class RefreshCron(threading.Thread):
    def __init__(self, interval, app):
        threading.Thread.__init__(self, name='refresh-cron')
        self.setDaemon(True)

        self._stopped = threading.Event()

        self.interval = interval
        self.app = app

    def run(self):
        while not self._stopped.wait(self.interval):
            try:
                self._do_refresh()
            except Exception as e:
                logger.error('refresh cron failed', e)

    def _do_refresh(self):
        self.app.config['CACHE'].clear()
        self.app.config['METADATA'].refresh_metadata()

        deletions = 0
        temp = self.app.config['TEMP']
        for name in os.listdir(temp):
            path = os.path.join(temp, name)
            age = time.time() - os.stat(path).st_mtime
            if age > self.interval:
                if os.path.isfile(path) or os.path.islink(path):
                    os.remove(path)
                else:
                    shutil.rmtree(path)
                deletions = deletions + 1

        logger.info('cleared cache, refreshed metadata and deleted %s expired temporary files', deletions)


def create_application(debug=False, verbose=False):
    """
    Creates fully configured flask application

    :param debug: Launch the app in debug-mode.
    :param verbose: True enables logging,
                    None (default) only enables logging if not in debug mode
                    False no logging configured.
    :return: The created Flask application
    """
    import gladweb.config

    app = Flask(__name__)
    app.config.from_object('gladweb.config')
    app.debug = debug
    app.freezer = Freezer(app)

    if not os.path.exists(app.config['TEMP']):
        os.makedirs(app.config['TEMP'])

    if verbose or (not app.debug and verbose is None):
        setup_logging()

    if sentry is not None:
        sentry.init_app(app, logging=True, level=logging.WARN)

    if app.config['CRON'] > 0:
        cron = RefreshCron(app.config['CRON'], app)
        cron.start()

    @app.before_request
    def before_request():
        g.cache = app.config['CACHE']
        g.opener = app.config['OPENER']
        g.metadata = app.config['METADATA']

    from gladweb.views.index import index
    app.register_blueprint(index)

    from gladweb.views.generated import generated
    idx = AutoIndexBlueprint(generated,
                             browse_root=app.config['TEMP'],
                             add_url_rules=False,
                             silk_options={'silk_path': '/icons'})

    @generated.route('/<root>/')
    @generated.route('/<root>/<path:path>')
    def autoindex(root, path='.'):
        root = werkzeug.utils.secure_filename(root)
        browse_root = os.path.join(app.config['TEMP'], root)
        data_path = os.path.join(browse_root, '.data')
        if os.path.exists(data_path):
            with open(data_path) as fobj:
                g.data = json.load(fobj)
        return idx.render_autoindex(
            path,
            browse_root=browse_root,
            template='autoindex.html',
            template_context={'root': root}
        )

    app.register_blueprint(generated, url_prefix='/generated')

    app.jinja_env.filters['pretty_date'] = gladweb.util.pretty_date
    app.jinja_env.globals.update(glad_version=glad.__version__)

    return app
