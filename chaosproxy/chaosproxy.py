import SimpleHTTPServer
import copy
import json
import urllib2
from urlparse import urljoin

import logging

import time

from configuration import Configuration

__version__ = '0.0.1'


class DropResponseBuffer:
    def __init__(self, stream=None):
        self.stream = stream
        self.code = 200
        self.headers = {dict: {}}

    def read(self, length=0):
        if self.stream:
            logging.debug("Response received: %s", self.stream.read())
            self.stream.close()
        else:
            logging.debug("No response here")


class ChaosProxy:
    configuration = Configuration({})

    def __init__(self, config):
        ChaosProxy.configuration = config

    @staticmethod
    def short_unique_id():
        return str(hex(int(time.time() * 999999))[2:])

    class Proxy(SimpleHTTPServer.SimpleHTTPRequestHandler):

        server_version = "ChaosServer/" + __version__

        def __do_proxy(self):
            req_id = ChaosProxy.short_unique_id()
            logging.debug('New request received: %s', req_id)
            # hijack request and change url
            url = urljoin(ChaosProxy.configuration.get_remotehost(), self.path)
            logging.debug('Request: %s - Forwarding to %s', req_id, url)
            # chaos configuration
            request_delay = ChaosProxy.configuration.get_request_delay()
            response_delay = ChaosProxy.configuration.get_response_delay()
            request_drop = ChaosProxy.configuration.is_drop_request_enabled()
            response_drop = ChaosProxy.configuration.is_drop_response_enabled()
            # keep same body of the original request
            body = None
            if self.headers.getheader('content-length') is not None:
                content_len = int(self.headers.getheader('content-length'))
                body = self.rfile.read(content_len)
            # keep same headers from the original request
            new_headers = copy.copy(self.headers)
            new_headers['ChaosProxyHost'] = self.address_string()
            try:
                del new_headers['accept-encoding']
            except KeyError:
                pass
            # remove host from headers, otherwise the request will be refused by almost all servers
            if new_headers.get('host'):
                del new_headers['host']
            # send request
            try:
                response = self.__do_request(
                    url, body, new_headers, req_id, request_delay, response_delay, request_drop, response_drop
                )
                self.response_code = response.code
                # add new headers with information
                self.headers = copy.copy(response.headers)
                self.headers['ChaosProxyHost'] = self.address_string()
                self.headers['ChaosProxyWillDropRequest'] = str(request_drop)
                self.headers['ChaosProxyWillDropResponse'] = str(response_drop)
                self.headers['ChaosProxyWillDelayRequest'] = str(request_delay) + (' s' if request_delay else '')
                self.headers['ChaosProxyWillDelayResponse'] = str(response_delay) + (' s' if response_delay else '')
                logging.debug('Request: %s - Request Headers:\n%s', req_id,
                              json.dumps(response.headers, indent=2))
                self.send_head()
                self.copyfile(response, self.rfile)
                self.rfile.close()
            except IOError, e:
                logging.error("Request: %s - Oops something went wrong: %s", req_id, e)

            logging.debug('Request processed: %s', req_id)

        def send_head(self):
            try:
                self.send_response(self.response_code)
                for header, value in self.headers.dict.iteritems():
                    if "transfer-encoding" == header or "connection" == header:
                        continue
                    self.send_header(header, value)
                self.end_headers()
            except:
                raise

        @staticmethod
        def __do_request(url, body, headers, req_id, request_delay, response_delay, request_drop, response_drop):
            req = urllib2.Request(url, body, headers)
            try:
                logging.debug('Request: %s - Request Headers:\n%s', req_id, headers)
                logging.debug('Request: %s - Request Body:\n%s', req_id, body)
                if request_drop:
                    logging.debug('Request: %s - Request to %s dropped...', req_id, url)
                    return DropResponseBuffer()  # drop request
                if request_delay:
                    time.sleep(request_delay)  # delay x seconds
                response = urllib2.urlopen(req)
            except urllib2.URLError, e:
                logging.error("Request: %s - Oops something went wrong: %s", req_id, e)
                response = DropResponseBuffer()
            if response_drop:
                logging.debug('Request: %s - Response from %s dropped...', req_id, url)
                return DropResponseBuffer(response)  # drop response
            if response_delay:
                time.sleep(response_delay)  # delay x seconds
            return response

        def do_GET(self):
            self.__do_proxy()

        def do_POST(self):
            self.__do_proxy()

        def do_PUT(self):
            self.__do_proxy()

        def do_PATCH(self):
            self.__do_proxy()

        def do_DELETE(self):
            self.__do_proxy()

        def do_COPY(self):
            self.__do_proxy()
