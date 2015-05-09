import argparse
from gladweb import create_application


def main():
    parser = argparse.ArgumentParser('gladweb')
    parser.add_argument('--port', default=5000, help='Port to listen on.')
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind to.')
    parser.add_argument('--debug', action='store_true', help='TESTING ONLY')
    ns = parser.parse_args()

    app = create_application()
    app.run(
        debug=ns.debug, port=int(ns.port), host=ns.host
    )


if __name__ == '__main__':
    main()