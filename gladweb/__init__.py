from flask import Flask, g
from gladweb.metadata import Metadata
import gladweb.util
import logging
import sys


class LevelFilter(logging.Filter):
    def __init__(self, levels):
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

    root_logger.setLevel(logging.DEBUG)


def get_glad_version():
    try:
        import pkg_resources
    except ImportError:
        return 'Unknown'

    return pkg_resources.get_distribution('glad').version


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
    app.config['METADATA'] = Metadata(app.config['CACHE'])
    app.debug = debug

    if verbose or (not app.debug and verbose is None):
        setup_logging()

    @app.before_request
    def before_request():
        g.cache = app.config['CACHE']
        g.metadata = app.config['METADATA']

    from gladweb.views.index import index
    app.register_blueprint(index)

    app.jinja_env.filters['pretty_date'] = gladweb.util.pretty_date
    app.jinja_env.globals.update(glad_version=get_glad_version())

    return app