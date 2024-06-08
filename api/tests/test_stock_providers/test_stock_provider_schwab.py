# pylint:disable=missing-module-docstring, invalid-name, line-too-long
# pylint:disable=missing-function-docstring

import os
import unittest

from core.utils import DotDict
from unittest.mock import Mock, patch

from stock_providers.schwab import Schwab
from test_stock_providers.fixtures import api_fixtures

class Test_StockProviderSchwab_Schwab(unittest.TestCase):

    def setUp(self):
        os.environ['SCHWAB_API_KEY'] = 'key'
        os.environ['SCHWAB_API_SECRET'] = 'secret'
        os.environ['SCHWAB_ACCESS_TOKEN'] = 'secret'

    def tearDown(self):
        del os.environ['SCHWAB_API_KEY']
        del os.environ['SCHWAB_API_SECRET']
        del os.environ['SCHWAB_ACCESS_TOKEN']

    @patch('stock_providers.schwab.requests')
    def test_price_history_returns_expected_values(self, mock_requests):
        expected_stock_quote = api_fixtures.schwab_price_history_api_response_success()
        mock_requests.get.return_value.json.return_value = expected_stock_quote
        schwab = Schwab()
        actual_stock_quote = schwab.price_history('aapl', '10daily', '1year')

        self.assertDictEqual(actual_stock_quote, expected_stock_quote)

    @patch('stock_providers.schwab.requests')
    def test_price_history_calls_expected_endpoint(self, mock_requests):
        polygon = Schwab()
        polygon.price_history('aapl', '10daily', '1year', '1717778681000', '1717778681000', False)

        mock_requests.get.assert_called_with(
            ''.join([
                'https://api.schwabapi.com/marketdata/v1/pricehistory?symbol=AAPL&periodType=1&',
                'period=year&frequencyType=10&frequency=daily&startDate=1717778681000&',
                'endDate=1717778681000&needExtendedData=false&needPreviousClose=true',
            ]),
            timeout=5
        )

    @patch('stock_providers.schwab.requests')
    def test_price_history_calls_expected_endpoint_with_only_relevant_params(self, mock_requests):
        polygon = Schwab()
        polygon.price_history('aapl', '10daily', '1year')

        mock_requests.get.assert_called_with(
            ''.join([
                'https://api.schwabapi.com/marketdata/v1/pricehistory?symbol=AAPL&periodType=1',
                '&period=year&frequencyType=10&frequency=daily',
                '&needExtendedData=false&needPreviousClose=true'
            ]),
            timeout=5
        )