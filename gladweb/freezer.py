from flask import url_for
import os


class Freezer(object):
    def __init__(self, app=None):
        self.app = None
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app

    def freeze(self, name):
        client = self.app.test_client()

        path = os.path.join(self.app.config['TEMP'], name)
        rel_paths = list()
        for root, dirs, files in os.walk(path):
            rel_paths.append(os.path.relpath(root, path))

        for rel_path in rel_paths:
            response = client.get(url_for('generated.autoindex', root=name, path=rel_path))
            with open(os.path.join(path, rel_path, 'index.html'), 'wb') as f:
                f.write(response.data)
