# pylint:disable=missing-module-docstring, missing-class-docstring
# pylint:disable=missing-function-docstring, invalid-name, line-too-long

import unittest

from pathlib import Path

from core.config import Config
from core.config import InvalidEnvironentError
from core.config import Environment
from core.utils import DotDict

class TestConfig_Config(unittest.TestCase):

    test_config_fixture_path_pattern = Path(__file__).parent / Path('fixtures', 'test_config_{0}.yml')

    def test_to_dotdict_returns_dotdict_instance(self):
        Config.config_file_path_pattern = TestConfig_Config.test_config_fixture_path_pattern
        actual_config = Config(Environment.DEV.value).to_dotdict()
        self.assertIsInstance(actual_config, DotDict)

    def test_to_dict_returns_dict_instance(self):
        Config.config_file_path_pattern = TestConfig_Config.test_config_fixture_path_pattern
        actual_config = Config(Environment.DEV.value).to_dict()
        self.assertIsInstance(actual_config, dict)

    def test_to_dotdict_returns_default_config_if_config_file_path_not_passed(self):
        actual_config = Config(Environment.DEV.value).to_dotdict()
        self.assertIsInstance(actual_config, DotDict)

    def test_raises_for_invalid_environment(self):
        with self.assertRaises(InvalidEnvironentError):
            Config('invalid-env')

    def test_can_be_used_as_dictionary(self):
        Config.config_file_path_pattern = TestConfig_Config.test_config_fixture_path_pattern
        actual_value = Config(Environment.DEV.value)['MySection']['key']
        expected_value = 'value'
        self.assertEqual(actual_value, expected_value)
