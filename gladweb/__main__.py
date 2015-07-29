import argparse
import sys
from gladweb import create_application


def init(ns):
    import gladweb.config
    from gladweb.metadata import Metadata

    cache = gladweb.config.CACHE
    cache.clear()

    # refreshes the metadata, since the cache is empty
    Metadata(cache)


def www(ns):
    app = create_application(debug=ns.debug, verbose=ns.verbose)
    app.run(port=int(ns.port), host=ns.host)


def main():
    parser = argparse.ArgumentParser('gladweb')
    subparsers = parser.add_subparsers(dest='subparser_name')

    init_parser = subparsers.add_parser('init')

    www_parser = subparsers.add_parser('www')
    www_parser.add_argument('--port', default=5000, help='Port to listen on.')
    www_parser.add_argument('--host', default='127.0.0.1', help='Host to bind to.')
    www_parser.add_argument('--debug', action='store_true', help='TESTING ONLY')
    www_parser.add_argument('--verbose', action='store_true', help='Log to stdout and stderr')

    ns = parser.parse_args()

    func = getattr(sys.modules[__name__], ns.subparser_name)
    func(ns)


if __name__ == '__main__':
    main()
