import argparse
from gladweb import create_application


def main():
    parser = argparse.ArgumentParser('gladweb')
    parser.add_argument('--port', default=5000, help='Port to listen on.')
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind to.')
    parser.add_argument('--debug', action='store_true', help='TESTING ONLY')
    parser.add_argument('--verbose', action='store_true', help='Log to stdout and stderr')
    ns = parser.parse_args()

    app = create_application(debug=ns.debug, verbose=ns.verbose)
    app.run(port=int(ns.port), host=ns.host)


if __name__ == '__main__':
    main()