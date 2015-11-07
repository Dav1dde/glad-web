from flask import Flask, g
from flask.ext.autoindex import AutoIndexBlueprint
import werkzeug
import glad
from gladweb.metadata import Metadata
import gladweb.util
import logging
import sys
import os


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

    if not os.path.exists(app.config['TEMP']):
        os.makedirs(app.config['TEMP'])

    if verbose or (not app.debug and verbose is None):
        setup_logging()

    @app.before_request
    def before_request():
        g.cache = app.config['CACHE']
        g.metadata = Metadata(g.cache)

    from gladweb.views.index import index
    app.register_blueprint(index)

    from gladweb.views.generated import generated
    idx = AutoIndexBlueprint(generated, browse_root=app.config['TEMP'], add_url_rules=False)

    @generated.route('/<root>/')
    @generated.route('/<root>/<path:path>')
    def autoindex(root, path='.'):
        root = werkzeug.utils.secure_filename(root)
        browse_root = os.path.join(app.config['TEMP'], root)
        serialized_path = os.path.join(browse_root, '.serialized')
        if os.path.exists(serialized_path):
            with open(serialized_path) as fobj:
                g.serialized = fobj.read().strip()
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
