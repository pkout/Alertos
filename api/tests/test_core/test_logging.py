# pylint:disable=missing-module-docstring, missing-class-docstring
# pylint:disable=missing-function-docstring, invalid-name, line-too-long

import logging
import unittest
from unittest.mock import patch

from core.logging import get_logger
from core.utils import DotDict

class TestUtils(unittest.TestCase):

    @patch('stock_producer.config', DotDict({
        'Logging': {
            'Format': '%(asctime)s [%(name)s] %(levelname)-8s %(message)s',
            'Level': 'DEBUG'
        }
    }))
    def test_returns_logger_instance_with_expected_log_level(self):
        actual_logger = get_logger(__name__)
        self.assertIsInstance(actual_logger, logging.Logger)
        self.assertEqual(actual_logger.level, logging.DEBUG)