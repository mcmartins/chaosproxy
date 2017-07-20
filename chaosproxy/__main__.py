#!/usr/bin/env python
# -*- coding: utf-8 -*-
import SocketServer
import argparse
import atexit
import logging
import datetime
import traceback
import ssl

import StringIO

import configuration

from signal import signal, SIGTERM
from chaosproxy import ChaosProxy


@atexit.register
def __cleanup():
    logging.info('Bye Bye')


def traceback_exception_handler():

    def log_unhandled_exception(etype, value, tb, limit=None, file=None):
        tb_output = StringIO.StringIO()
        traceback.print_tb(tb, limit, tb_output)
        logging.warn(tb_output.getvalue())
        tb_output.close()

    traceback.print_exception = log_unhandled_exception


if __name__ == '__main__':
    # global exception hook
    traceback_exception_handler()

    # arguments parser
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
    protocol = "http"
    if "https" in config.get_remotehost().lower():
        protocol = "https"
        server.socket = ssl.wrap_socket(server.socket, certfile="cert/server.crt", keyfile="cert/server.key", server_side=True)

    logging.info('Listening on [%s]', protocol + '://' + ':'.join(map(str, config.get_localhost())))
    logging.info('Forwarding to [%s]', config.get_remotehost())

    # start server
    server.serve_forever()
