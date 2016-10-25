import random
import os
import json
import logging


class Configuration:
    def __init__(self, config):
        self.configuration = self.__parse(config)

    @staticmethod
    def __parse(config_file):
        if config_file:
            logging.info('Parsing configuration...')
            if os.path.isfile(config_file):
                config_file = json.loads(open(config_file).read().decode("utf-8"))
            else:
                try:
                    config_file = json.JSONEncoder().encode(json.loads(json.dumps(config_file)))
                except AttributeError:
                    raise Exception('Input provided is not an existing file or valid JSON string!')
            logging.debug('Configuration input is: %s', json.dumps(config_file, indent=2))
            return config_file

    def get_localhost(self):
        return (
            self.configuration.get('local').get('host'),
            self.configuration.get('local').get('port')
        )

    def get_remotehost(self):
        return self.configuration.get('remote').get('host')

    def is_drop_request_enabled(self):
        if self.configuration.get('connection').get('request').get('dropRandomly'):
            return random.randint(1, 5000) % 3 == 0
        return False

    def is_drop_response_enabled(self):
        if self.configuration.get('connection').get('response').get('dropRandomly'):
            return random.randint(1, 5000) % 3 == 0
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
            i = self.configuration.get('connection').get('request').get('delay').get('random').get('min', 0)
            e = self.configuration.get('connection').get('request').get('delay').get('random').get('max', 0)
            return float(random.randint(i, e)) / float(1000)
        elif self.configuration.get('connection').get('request').get('delay') \
                and self.configuration.get('connection').get('request').get('delay').get('logNormal'):
            sigma = self.configuration.get('connection').get('request').get('delay').get('logNormal').get('sigma')
            mean = self.configuration.get('connection').get('request').get('delay').get('logNormal').get('mean')
            return float(round(random.gauss(mean, sigma))) / float(1000)
        elif self.configuration.get('connection').get('request').get('delay') \
                and self.configuration.get('connection').get('request').get('delay').get('fixed'):
            return float(self.configuration.get('connection').get('request').get('delay').get('fixed')) / float(1000)
        else:
            return False

    def get_response_delay(self):
        if self.configuration.get('connection').get('response').get('delay') \
                and self.configuration.get('connection').get('response').get('delay').get('random'):
            i = self.configuration.get('connection').get('response').get('delay').get('random').get('min', 0)
            e = self.configuration.get('connection').get('response').get('delay').get('random').get('max', 0)
            return float(random.randint(i, e)) / float(1000)
        elif self.configuration.get('connection').get('response').get('delay') \
                and self.configuration.get('connection').get('response').get('delay').get('logNormal'):
            sigma = self.configuration.get('connection').get('response').get('delay').get('logNormal').get('sigma')
            mean = self.configuration.get('connection').get('response').get('delay').get('logNormal').get('mean')
            return float(round(random.gauss(mean, sigma))) / float(1000)
        elif self.configuration.get('connection').get('response').get('delay') \
                and self.configuration.get('connection').get('response').get('delay').get('fixed'):
            return float(self.configuration.get('connection').get('response').get('delay').get('fixed')) / float(1000)
        else:
            return False
