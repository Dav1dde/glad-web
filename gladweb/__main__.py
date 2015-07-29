import argparse
import shutil
import sys
import time
from gladweb import create_application
import os


def init(ns):
    import gladweb.config

    _refresh_metadata(gladweb.config.CACHE)


def _refresh_metadata(cache, diff=60):
    from gladweb.metadata import Metadata

    m = Metadata(cache)
    if time.time() - m.created > diff:
        cache.clear()
        m.refresh_metadata()


def www(ns):
    app = create_application(debug=ns.debug, verbose=ns.verbose)
    app.run(port=int(ns.port), host=ns.host)


def cron(ns):
    import gladweb.config

    diff = ns.age * 60 * 60 if ns.age >= 0 else 0
    _refresh_metadata(gladweb.config.CACHE, diff)

    if ns.age < 0:
        return

    temp = gladweb.config.TEMP
    for name in os.listdir(temp):
        path = os.path.join(temp, name)
        mtime = os.stat(path).st_mtime
        age = time.time() - mtime
        hours = age / 60 / 60
        if hours > ns.age:
            if os.path.isfile(path) or os.path.islink(path):
                os.remove(path)
            else:
                shutil.rmtree(path)


def main():
    parser = argparse.ArgumentParser('gladweb')
    subparsers = parser.add_subparsers(dest='subparser_name')

    init_parser = subparsers.add_parser('init')

    www_parser = subparsers.add_parser('www')
    www_parser.add_argument('--port', default=5000, help='Port to listen on.')
    www_parser.add_argument('--host', default='127.0.0.1', help='Host to bind to.')
    www_parser.add_argument('--debug', action='store_true', help='TESTING ONLY')
    www_parser.add_argument('--verbose', action='store_true', help='Log to stdout and stderr')

    cron_parser = subparsers.add_parser('cron')
    cron_parser.add_argument('--age', type=int, default=24,
                             help='Temporary files will be deleted after X hours')

    ns = parser.parse_args()

    func = getattr(sys.modules[__name__], ns.subparser_name)
    func(ns)


if __name__ == '__main__':
    main()
