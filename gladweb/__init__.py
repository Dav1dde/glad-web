from flask import Flask, g
from gladweb.metadata import Metadata
import gladweb.util


def create_application():
    import gladweb.config

    app = Flask(__name__)
    app.config.from_object('gladweb.config')
    app.config['METADATA'] = Metadata(app.config['CACHE'])

    @app.before_request
    def before_request():
        g.cache = app.config['CACHE']
        g.metadata = app.config['METADATA']

    from gladweb.views.index import index
    app.register_blueprint(index)

    app.jinja_env.filters['pretty_date'] = gladweb.util.pretty_date

    return app