import unittest

from chaosproxy.configuration import Configuration


class ConfigurationTest(unittest.TestCase):
    def test_invalid_json(self):
        Configuration().get_localhost()


if __name__ == '__main__':
    unittest.main()
