#!/usr/bin/env python
# -*- coding: utf-8 -*-
import SocketServer
import argparse
import logging
import datetime
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
    args_parser.add_argument('-p', '--pathlogfile', help='path to store the log file', action='store',
                             dest='path_log_file', required=False)

    args = args_parser.parse_args()

    # set basic logging config
    if args.path_log_file:
        handler = logging.FileHandler(
            '{0}/ChaosProxy-{1}.log'.format(args.path_log_file, datetime.datetime.now().strftime('%Y%m%d')))
        formatter = logging.Formatter('%(asctime)s - [%(levelname)s] - %(message)s')
        handler.setFormatter(formatter)
        logging.getLogger().addHandler(handler)
    else:
        logging.basicConfig(format='%(asctime)s - [%(levelname)s] - %(message)s', level=logging.INFO)

    # set debug logging
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    logging.info('Initializing ChaosProxy')

    # parse configuration
    config = configuration.Configuration(args.input)

    # initialize server
    server = SocketServer.ThreadingTCPServer(config.get_localhost(), ChaosProxy(config).Proxy)
    server.daemon_threads = True
    server.allow_reuse_address = True
    logging.info('Listening on [%s]', 'http://' + ':'.join(map(str, config.get_localhost())))
    logging.info('Forwarding to [%s]', config.get_remotehost())

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logging.info('Stopping ChaosProxy')
        sys.exit(1)
