import unittest

from pathlib import Path

from core.config import Config
from core.config import ConfigFileNotFoundError
from core.utils import DotDict

class TestConfig_Config(unittest.TestCase):

    def test_to_dict_returns_config_dict(self):
        config_file_path = Path(__file__).parent.joinpath('fixtures', 'config.yml')

        actual_config = Config(config_file_path).to_dict()

        self.assertIsInstance(actual_config, DotDict)

    def test_raises_if_config_file_not_found(self):
        config_file_path = '/tmp/wrong/path'

        with self.assertRaises(ConfigFileNotFoundError):
            Config(config_file_path)