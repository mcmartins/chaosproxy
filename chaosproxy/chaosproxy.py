import SimpleHTTPServer
import copy
import urllib2
import logging
import time

import message

from urlparse import urljoin

from configuration import Configuration

__version__ = '0.0.1'


class DummyResponse:
    class DummyHeader(dict):
        def __init__(self, **kwargs):
            super(DummyResponse.DummyHeader, self).__init__(**kwargs)
            self.dict = dict()

    def __init__(self, req_id, stream=None):
        self.id = req_id
        self.stream = stream
        self.code = 500
        self.headers = stream.headers if stream else DummyResponse.DummyHeader()

    def read(self, length=0):
        if self.stream:
            logging.debug("%s - Response dropped received:\n%s", self.id, message.format(self.stream.read()))
            self.stream.close()
        else:
            logging.debug('%s - Response body:\n{}', self.id)


class ChaosProxy:
    configuration = Configuration({})

    def __init__(self, config):
        ChaosProxy.configuration = config

    @staticmethod
    def short_unique_id():
        return str(hex(int(time.time() * 999999))[2:])

    class Proxy(SimpleHTTPServer.SimpleHTTPRequestHandler):

        server_version = 'ChaosServer/' + __version__

        def __do_proxy(self):
            req_id = ChaosProxy.short_unique_id()
            logging.info('%s - Request received', req_id)
            # hijack request and change url
            url = urljoin(ChaosProxy.configuration.get_remotehost(), self.path)
            logging.info('%s - Forwarding request to [%s]', req_id, url)
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
            new_headers['ChaosProxy-Host'] = self.address_string()
            new_headers['ChaosProxy-RequestId'] = req_id
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
                self.send_head()
                self.copyfile(response, self.rfile)
                self.rfile.close()
            except IOError, e:
                logging.error('%s - Oops something went wrong: %s', req_id, e)

            logging.info('%s - Request processed', req_id)

        def __do_request(self, url, body, headers, req_id, request_delay, response_delay, request_drop, response_drop):
            req = urllib2.Request(url, body, headers)
            try:
                logging.debug('%s - Request headers:\n%s', req_id, message.format(headers.dict))
                logging.debug('%s - Request body:\n%s', req_id, message.format(body))
                if request_drop:
                    logging.info('%s - Dropped request to [%s]', req_id, url)
                    return DummyResponse(req_id)  # drop request
                if request_delay:
                    time.sleep(request_delay)  # delay x seconds
                response = urllib2.urlopen(req)
            except urllib2.URLError, e:
                logging.error('%s - Oops something went wrong:\n%s', req_id, e)
                response = DummyResponse(req_id)
            if response_drop:
                logging.info('%s - Dropped response from [%s]', req_id, url)
                response = DummyResponse(req_id, response)  # drop response
            if response_delay:
                time.sleep(response_delay)  # delay x seconds
            # add new headers with information
            self.headers = copy.copy(response.headers)
            self.headers['ChaosProxy-Host'] = self.address_string()
            self.headers['ChaosProxy-RequestId'] = req_id
            self.headers['ChaosProxy-Drop-Request'] = str(request_drop)
            self.headers['ChaosProxy-Drop-Response'] = str(response_drop)
            self.headers['ChaosProxy-Delay-Request'] = str(request_delay) + (' s' if request_delay else '')
            self.headers['ChaosProxy-Delay-Response'] = str(response_delay) + (' s' if response_delay else '')
            logging.debug('%s - Response headers:\n%s', req_id, message.format(response.headers.dict))
            return response

        def send_head(self):
            try:
                self.send_response(self.response_code)
                for header, value in self.headers.dict.iteritems():
                    # do not send back the following headers
                    if 'transfer-encoding' == header or 'connection' == header:
                        continue
                    self.send_header(header, value)
                self.end_headers()
            except:
                raise

        def send_response(self, code, message=None):
            if message is None:
                if code in self.responses:
                    message = self.responses[code][0]
                else:
                    message = ''
            if self.request_version != 'HTTP/0.9':
                self.wfile.write('%s %d %s\r\n' % (self.protocol_version, code, message))
            self.send_header('Server', self.version_string())
            self.send_header('Date', self.date_time_string())

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
