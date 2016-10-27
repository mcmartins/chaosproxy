import os
import json
import logging
import stats


class Configuration:
    """
    Handles a json string or file and generates its representative Configuration object
    """

    def __init__(self, config):
        self.configuration = self.__parse(config)

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

    def get_localhost(self):
        return 'localhost', self.configuration.get('local').get('port')

    def get_remotehost(self):
        return self.configuration.get('remote').get('host')

    def is_drop_request_enabled(self):
        if self.configuration.get('connection').get('request').get('dropRandomly'):
            return stats.__random(1, 5000) % 3 == 0
        return False

    def is_drop_response_enabled(self):
        if self.configuration.get('connection').get('response').get('dropRandomly'):
            return stats.__random(1, 5000) % 3 == 0
        return False

    def is_delay_request_enabled(self):
        return self.configuration.get('connection').get('request').get('delay') \
               and (
                   self.configuration.get('connection').get('request').get('delay').get('random') or
                   self.configuration.get('connection').get('request').get('delay').get('logNormal') or
                   self.configuration.get('connection').get('request').get('delay').get('fixed')
               )

    def is_delay_response_enabled(self):
        return self.configuration.get('connection').get('response').get('delay') \
               and (
                   self.configuration.get('connection').get('response').get('delay').get('random') or
                   self.configuration.get('connection').get('response').get('delay').get('logNormal') or
                   self.configuration.get('connection').get('response').get('delay').get('fixed')
               )

    def get_request_delay(self):
        if self.configuration.get('connection').get('request').get('delay') \
                and self.configuration.get('connection').get('request').get('delay').get('random'):
            a = self.configuration.get('connection').get('request').get('delay').get('random').get('min', 0)
            b = self.configuration.get('connection').get('request').get('delay').get('random').get('max', 0)
            return stats.__random(a, b) / float(1000)
        elif self.configuration.get('connection').get('request').get('delay') \
                and self.configuration.get('connection').get('request').get('delay').get('logNormal'):
            sigma = self.configuration.get('connection').get('request').get('delay').get('logNormal').get('sigma')
            mean = self.configuration.get('connection').get('request').get('delay').get('logNormal').get('mean')
            return stats.__log_normal(sigma=sigma, mean=mean) / float(1000)
        elif self.configuration.get('connection').get('request').get('delay') \
                and self.configuration.get('connection').get('request').get('delay').get('fixed'):
            return float(self.configuration.get('connection').get('request').get('delay').get('fixed')) / float(1000)
        else:
            return False

    def get_response_delay(self):
        if self.configuration.get('connection').get('response').get('delay') \
                and self.configuration.get('connection').get('response').get('delay').get('random'):
            a = self.configuration.get('connection').get('response').get('delay').get('random').get('min', 0)
            b = self.configuration.get('connection').get('response').get('delay').get('random').get('max', 0)
            return stats.__random(a, b) / float(1000)
        elif self.configuration.get('connection').get('response').get('delay') \
                and self.configuration.get('connection').get('response').get('delay').get('logNormal'):
            sigma = self.configuration.get('connection').get('response').get('delay').get('logNormal').get('sigma')
            mean = self.configuration.get('connection').get('response').get('delay').get('logNormal').get('mean')
            return stats.__log_normal(sigma=sigma, mean=mean) / float(1000)
        elif self.configuration.get('connection').get('response').get('delay') \
                and self.configuration.get('connection').get('response').get('delay').get('fixed'):
            return float(self.configuration.get('connection').get('response').get('delay').get('fixed')) / float(1000)
        else:
            return False
