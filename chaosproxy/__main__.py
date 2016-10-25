#!/usr/bin/env python
# -*- coding: utf-8 -*-
import SocketServer
import argparse
import logging
import sys

import configuration
from chaosproxy import ChaosProxy

if __name__ == '__main__':
    args_parser = argparse.ArgumentParser(
        description='Main entry point for ChaosProxy. Usage: python -m chaosproxy -v -i path/to/conf-file.json'
    )
    args_parser.add_argument('-v', '--verbose', help='increase output verbosity', action='store_true',
                             required=False)
    args_parser.add_argument('-i', '--input', help='input json file / object', action='store',
                             dest='input', required=True)

    args = args_parser.parse_args()

    # set basic logging config
    logging.basicConfig(format='%(asctime)s - [%(levelname)s] - %(message)s', level=logging.INFO)

    # set debug logging
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    logging.info('Initializing ChaosProxy...')

    # parse configuration
    config = configuration.Configuration(args.input)

    # initialize server
    server = SocketServer.ThreadingTCPServer(config.get_localhost(), ChaosProxy(config).Proxy)
    server.daemon_threads = True
    server.allow_reuse_address = True
    logging.info("ChaosProxy listening on [%s]", config.get_localhost())

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logging.info("Ctrl C - Stopping ChaosProxy")
        sys.exit(1)
