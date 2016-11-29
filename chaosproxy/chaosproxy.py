import SimpleHTTPServer
import copy
import urllib2
import logging
import time

import message

from urlparse import urljoin

__version__ = '0.0.1'


class ChaosProxy:
    configuration = None

    @staticmethod
    def get_short_unique_id():
        return str(hex(int(time.time() * 999999))[2:])

    def __init__(self, config):
        ChaosProxy.configuration = config

    class DummyResponse:
        class DummyHeader(dict):
            def __init__(self, **kwargs):
                super(ChaosProxy.DummyResponse.DummyHeader, self).__init__(**kwargs)
                self.dict = dict()

        def __init__(self, request_id, stream=None):
            self.id = request_id
            self.stream = stream
            self.code = 500
            self.headers = stream.headers if stream else ChaosProxy.DummyResponse.DummyHeader()

        def read(self, length=0):
            if self.stream:
                content_type = self.headers.getheader('content-type')
                logging.debug("%s - Response dropped received:\n%s", self.id,
                              message.format(self.stream.read(), content_type))
                self.stream.close()
            else:
                logging.debug('%s - Response body:\n{}', self.id)

        def close(self):
            if self.stream:
                self.stream.close()

    class Proxy(SimpleHTTPServer.SimpleHTTPRequestHandler):

        server_version = 'ChaosServer/' + __version__

        def __do_proxy(self, request_id):
            logging.info('%s - [%s] Request received', request_id, str(self.command))
            # hijack request and change url
            url = urljoin(ChaosProxy.configuration.get_remotehost(), self.path)
            logging.info('%s - Forwarding request to [%s]', request_id, url)
            # keep same headers from the original request
            new_headers = self.__handle_request_headers(request_id)
            # keep same body of the original request
            body = self.__handle_request_body(request_id)
            try:
                # create chaos configuration
                chaos = ChaosProxy.configuration.get_chaos_conf(self.path, body)
                # send request to remote host
                response = self.__do_request(url, body, new_headers, chaos, request_id)
                self.response_code = response.code
                self.send_head()
                self.copyfile(response, self.rfile)
                self.rfile.close()
                self.wfile.close()
            except IOError, e:
                logging.error('%s - Oops something went wrong: %s', request_id, e)

            logging.info('%s - [%s] Request processed', request_id, str(self.command))

        def __do_request(self, url, body, headers, chaos, request_id):
            req = urllib2.Request(url, body, headers)
            try:
                if chaos.get('request_drop'):
                    logging.info('%s - Request dropped', request_id)
                    return ChaosProxy.DummyResponse(request_id)  # drop request
                if chaos.get('request_delay'):
                    logging.info('%s - Request delaying for [%s s]', request_id, chaos.get('request_delay'))
                    time.sleep(chaos.get('request_delay'))  # delay x seconds
                response = urllib2.urlopen(req)
            except urllib2.URLError, e:
                logging.error('%s - Oops something went wrong:\n%s', request_id, e)
                response = ChaosProxy.DummyResponse(request_id)
            if chaos.get('response_drop'):
                logging.info('%s - Response dropped', request_id)
                response = ChaosProxy.DummyResponse(request_id, response)  # drop response
            if chaos.get('response_delay'):
                logging.info('%s - Response Delayed for [%s s]', request_id, chaos.get('response_delay'))
                time.sleep(chaos.get('response_delay'))  # delay x seconds
            # copy response headers and add new headers with chaos server info information
            self.__handle_response_headers(response, chaos, request_id)
            return response

        def __handle_request_body(self, request_id):
            if self.headers.getheader('content-length') is not None:  # yeah, in case the server just don't send this?
                content_len = int(self.headers.getheader('content-length'))
            else:
                content_len = 2048  # some big buffer
            body = self.rfile.read(content_len)
            content_type = self.headers.getheader('content-type')
            logging.debug('%s - Request body:\n%s', request_id, message.format(body, content_type))
            return body

        def __handle_request_headers(self, request_id):
            new_headers = copy.copy(self.headers)
            new_headers['ChaosProxy-Host'] = self.address_string()
            new_headers['ChaosProxy-RequestId'] = request_id
            # remove accept encoding from headers
            if new_headers.get('accept-encoding'):
                del new_headers['accept-encoding']
            # remove host from headers, otherwise the request will be refused by almost all servers
            if new_headers.get('host'):
                del new_headers['host']
            logging.debug('%s - Request headers:\n%s', request_id, message.format(new_headers.dict, message.JSON))
            return new_headers

        def __handle_response_headers(self, response, chaos, request_id):
            self.headers = copy.copy(response.headers)
            self.headers['ChaosProxy-Host'] = self.address_string()
            self.headers['ChaosProxy-RequestId'] = request_id
            self.headers['ChaosProxy-Drop-Request'] = str(chaos.get('request_drop'))
            self.headers['ChaosProxy-Drop-Response'] = str(chaos.get('response_drop'))
            self.headers['ChaosProxy-Delay-Request'] = \
                str(chaos.get('request_delay')) + (' s' if chaos.get('request_delay') else '')
            self.headers['ChaosProxy-Delay-Response'] = \
                str(chaos.get('response_delay')) + (' s' if chaos.get('response_delay') else '')
            self.headers['Server'] = self.version_string()
            self.headers['Date'] = self.date_time_string()
            logging.debug('%s - Response headers:\n%s', request_id, message.format(response.headers.dict, message.JSON))

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

        def do_GET(self):
            self.__do_proxy(ChaosProxy.get_short_unique_id())

        def do_POST(self):
            self.__do_proxy(ChaosProxy.get_short_unique_id())

        def do_PUT(self):
            self.__do_proxy(ChaosProxy.get_short_unique_id())

        def do_PATCH(self):
            self.__do_proxy(ChaosProxy.get_short_unique_id())

        def do_DELETE(self):
            self.__do_proxy(ChaosProxy.get_short_unique_id())

        def do_COPY(self):
            self.__do_proxy(ChaosProxy.get_short_unique_id())
