import os
import json
import logging

from timer import Timer
from stats import random_value, log_normal_value


class Configuration:
    """
    Handles a json string or file and generates its representative Configuration object
    """

    def __init__(self, config):
        self.configuration = self.__parse(config)
        self.__init_stability_timer()

    @staticmethod
    def __parse(config_file):
        if config_file:
            logging.info('Parsing configuration')
            if os.path.isfile(config_file):
                config_file = json.loads(open(config_file).read().decode('utf-8'))
            else:
                try:
                    config_file = json.JSONEncoder().encode(json.loads(json.dumps(config_file)))
                except AttributeError:
                    raise Exception('Input provided is not an existing file or valid JSON string!')
            logging.debug('Configuration input is:\n%s', json.dumps(config_file, indent=2))
            return config_file

    def __init_stability_timer(self):
        self.stability_timer = Timer(
            self.configuration.get('connection').get('stableInterval') / float(1000),
            self.configuration.get('connection').get('unstableInterval') / float(1000)
        )

    def __get_drop_request_timeout(self):
        if self.configuration.get('connection').get('request').get('dropRandomly'):
            return random_value(1, 5000) % 3 == 0
        return False

    def __get_drop_response_timeout(self):
        if self.configuration.get('connection').get('response').get('dropRandomly'):
            return random_value(1, 5000) % 3 == 0
        return False

    def __get_request_delay(self):
        if self.configuration.get('connection').get('request').get('delay') \
                and self.configuration.get('connection').get('request').get('delay').get('random'):
            a = self.configuration.get('connection').get('request').get('delay').get('random').get('min', 0)
            b = self.configuration.get('connection').get('request').get('delay').get('random').get('max', 0)
            return random_value(a, b) / float(1000)
        elif self.configuration.get('connection').get('request').get('delay') \
                and self.configuration.get('connection').get('request').get('delay').get('logNormal'):
            sigma = self.configuration.get('connection').get('request').get('delay').get('logNormal').get('sigma')
            mean = self.configuration.get('connection').get('request').get('delay').get('logNormal').get('mean')
            return log_normal_value(sigma=sigma, mean=mean) / float(1000)
        elif self.configuration.get('connection').get('request').get('delay') \
                and self.configuration.get('connection').get('request').get('delay').get('fixed'):
            return float(self.configuration.get('connection').get('request').get('delay').get('fixed')) / float(1000)
        else:
            return False

    def __get_response_delay(self):
        if self.configuration.get('connection').get('response').get('delay') \
                and self.configuration.get('connection').get('response').get('delay').get('random'):
            a = self.configuration.get('connection').get('response').get('delay').get('random').get('min', 0)
            b = self.configuration.get('connection').get('response').get('delay').get('random').get('max', 0)
            return random_value(a, b) / float(1000)
        elif self.configuration.get('connection').get('response').get('delay') \
                and self.configuration.get('connection').get('response').get('delay').get('logNormal'):
            sigma = self.configuration.get('connection').get('response').get('delay').get('logNormal').get('sigma')
            mean = self.configuration.get('connection').get('response').get('delay').get('logNormal').get('mean')
            return log_normal_value(sigma=sigma, mean=mean) / float(1000)
        elif self.configuration.get('connection').get('response').get('delay') \
                and self.configuration.get('connection').get('response').get('delay').get('fixed'):
            return float(self.configuration.get('connection').get('response').get('delay').get('fixed')) / float(1000)
        else:
            return False

    def __ignore_if_endpoint_in_ignore_list(self, endpoint):
        endpoints = self.configuration.get('connection').get('ignoreIfEndpointContains')
        endpoints = [] if not endpoints else endpoints
        matches = [e for e in endpoints if endpoint in e]
        if len(matches) > 0:
            logging.debug('Endpoint \'%s\' detected, ChaosProxy will not interfere with this one...',
                          ";".join(matches))
        return len(matches) > 0

    def __ignore_if_body_contains_string(self, body):
        strings = self.configuration.get('connection').get('ignoreIfBodyContains')
        strings = [] if not strings else strings
        matches = [s for s in strings if s in body]
        if len(matches) > 0:
            logging.debug('Strings \'%s\' detected in body, ChaosProxy will not interfere with this one...',
                          ";".join(matches))
        return len(matches) > 0

    def get_localhost(self):
        return 'localhost', self.configuration.get('local').get('port')

    def get_remotehost(self):
        return self.configuration.get('remote').get('host')

    def get_chaos_conf(self, endpoint, body):
        stable = self.stability_timer.is_in_stable_period() \
                 or self.__ignore_if_endpoint_in_ignore_list(endpoint) \
                 or self.__ignore_if_body_contains_string(body)
        return {
            'request_delay': False if stable else self.__get_request_delay(),
            'response_delay': False if stable else self.__get_response_delay(),
            'request_drop': False if stable else self.__get_drop_request_timeout(),
            'response_drop': False if stable else self.__get_drop_response_timeout(),
        }
