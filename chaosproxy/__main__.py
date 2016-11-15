#!/usr/bin/env python
# -*- coding: utf-8 -*-
import SocketServer
import argparse
import atexit
import logging
import datetime
import configuration

from signal import signal, SIGTERM
from chaosproxy import ChaosProxy


@atexit.register
def __cleanup():
    logging.info('Bye Bye')


if __name__ == '__main__':
    args_parser = argparse.ArgumentParser(
        description='Usage: python -m chaosproxy -v -i path/to/conf-file.json -p path/to/log'
    )
    args_parser.add_argument('-v', '--verbose', help='debug log', action='store_true', required=False)
    args_parser.add_argument('-i', '--input', help='input json file / object', action='store', dest='input',
                             required=True)
    args_parser.add_argument('-p', '--pathlogs', help='path to store log files, e.g. /home/user', action='store',
                             dest='path_logs', required=False)

    args = args_parser.parse_args()

    # exit listeners
    signal(SIGTERM, __cleanup)

    # set logging config
    if args.path_logs:
        handler = logging.FileHandler(
            '{0}/ChaosProxy-{1}.log'.format(args.path_logs, datetime.datetime.now().strftime('%Y%m%d')))
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

    # configure server
    server = SocketServer.ThreadingTCPServer(config.get_localhost(), ChaosProxy(config).Proxy)
    server.daemon_threads = True
    server.allow_reuse_address = True

    logging.info('Listening on [%s]', 'http://' + ':'.join(map(str, config.get_localhost())))
    logging.info('Forwarding to [%s]', config.get_remotehost())

    # start server
    server.serve_forever()
