import os
import json
import logging
import time

from timer import Timer
from stats import random_value, log_normal_value


class Configuration:
    """
    Handles a json string or file and generates its representative Configuration object
    """

    def __init__(self, config):
        self.configuration = self.__parse(config)
        self.__init_stable_timer()

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

    @staticmethod
    def get_short_unique_id():
        return str(hex(int(time.time() * 999999))[2:])

    def __init_stable_timer(self):
        self.stability_timer = Timer(
            self.configuration.get('connection').get('stableInterval'),
            self.configuration.get('connection').get('unstableInterval')
        )

    def __is_stable_period_active(self):
        if self.stability_timer.is_stable_period():
            return True
        return False

    def __is_drop_request_enabled(self):
        if self.configuration.get('connection').get('request').get('dropRandomly'):
            return random_value(1, 5000) % 3 == 0
        return False

    def __is_drop_response_enabled(self):
        if self.configuration.get('connection').get('response').get('dropRandomly'):
            return random_value(1, 5000) % 3 == 0
        return False

    def __is_delay_request_enabled(self):
        return self.configuration.get('connection').get('request').get('delay') \
               and (
                   self.configuration.get('connection').get('request').get('delay').get('random') or
                   self.configuration.get('connection').get('request').get('delay').get('logNormal') or
                   self.configuration.get('connection').get('request').get('delay').get('fixed')
               )

    def __is_delay_response_enabled(self):
        return self.configuration.get('connection').get('response').get('delay') \
               and (
                   self.configuration.get('connection').get('response').get('delay').get('random') or
                   self.configuration.get('connection').get('response').get('delay').get('logNormal') or
                   self.configuration.get('connection').get('response').get('delay').get('fixed')
               )

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

    def get_localhost(self):
        return 'localhost', self.configuration.get('local').get('port')

    def get_remotehost(self):
        return self.configuration.get('remote').get('host')

    def get_chaos_conf(self):
        return {
            'remote_host': self.get_remotehost(),
            'request_delay': False if self.__is_stable_period_active() else self.__get_request_delay(),
            'response_delay': False if self.__is_stable_period_active() else self.__get_response_delay(),
            'request_drop': False if self.__is_stable_period_active() else self.__is_drop_request_enabled(),
            'response_drop': False if self.__is_stable_period_active() else self.__is_drop_response_enabled(),
            'request_id': self.get_short_unique_id()
        }
