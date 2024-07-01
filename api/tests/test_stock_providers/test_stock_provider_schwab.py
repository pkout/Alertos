# pylint:disable=missing-module-docstring, invalid-name, line-too-long
# pylint:disable=missing-function-docstring

import os
import unittest

from unittest.mock import Mock, patch

from stock_providers.schwab import Schwab
from stock_providers.exceptions import UnauthorizedError
from stock_providers.exceptions import UnableToRetrieveStockDataError
from test_stock_providers.fixtures import api_fixtures
from test_stock_providers.doubles.schwab import SchwabUnauthorizedStub
from test_stock_providers.doubles.schwab import SchwabReauthorizedStub
from test_stock_providers.doubles.schwab import SchwabJsonDecoderErrorStub

class Test_StockProviderSchwab_Schwab(unittest.TestCase):

    def setUp(self):
        os.environ['SCHWAB_API_KEY'] = 'key'
        os.environ['SCHWAB_API_SECRET'] = 'secret'
        os.environ['SCHWAB_ACCESS_TOKEN'] = 'secret'
        os.environ['SCHWAB_REFRESH_TOKEN'] = 'secret'

    def tearDown(self):
        del os.environ['SCHWAB_API_KEY']
        del os.environ['SCHWAB_API_SECRET']
        del os.environ['SCHWAB_ACCESS_TOKEN']
        del os.environ['SCHWAB_REFRESH_TOKEN']

    @patch('stock_providers.schwab.requests')
    def test_price_history_returns_expected_values(self, mock_requests):
        expected_stock_quote = api_fixtures.schwab_price_history_api_response_success()
        mock_requests.get.return_value.json.return_value = expected_stock_quote
        schwab = Schwab()
        actual_stock_quote = schwab.price_history('aapl', '10daily', '1year')

        self.assertDictEqual(actual_stock_quote, expected_stock_quote)

    @patch('stock_providers.schwab.requests')
    def test_price_history_calls_expected_endpoint(self, mock_requests):
        schwab = Schwab()
        schwab.price_history('aapl', '10daily', '1year', '1717778681000', '1717778681000', False)

        mock_requests.get.assert_called_with(
            ''.join([
                'https://api.schwabapi.com/marketdata/v1/pricehistory?symbol=AAPL&periodType=year&',
                'period=1&frequencyType=daily&frequency=10&startDate=1717778681000&',
                'endDate=1717778681000&needExtendedData=false&needPreviousClose=true',
            ]),
            timeout=5,
            headers={'Authorization': 'Bearer secret'}
        )

    @patch('stock_providers.schwab.requests')
    def test_price_history_calls_expected_endpoint_with_only_relevant_params(self, mock_requests):
        schwab = Schwab()
        schwab.price_history('aapl', '10daily', '1year')

        mock_requests.get.assert_called_with(
            ''.join([
                'https://api.schwabapi.com/marketdata/v1/pricehistory?symbol=AAPL&periodType=year',
                '&period=1&frequencyType=daily&frequency=10',
                '&needExtendedData=false&needPreviousClose=true'
            ]),
            timeout=5,
            headers={'Authorization': 'Bearer secret'}
        )

    def test_price_history_raises_unauthorized_if_server_responds_with_401_status_code(self):
        schwab = SchwabUnauthorizedStub()

        with self.assertRaises(UnauthorizedError):
            schwab.price_history('aapl', '10daily', '1year')

    @patch('stock_providers.schwab.requests')
    def test_quotes_calls_expected_endpoint(self, mock_requests):
        schwab = Schwab()
        schwab.quotes(['aapl', 'msft'])

        mock_requests.get.assert_called_with(
            'https://api.schwabapi.com/marketdata/v1/quotes?symbols=AAPL,MSFT',
            timeout=5,
            headers={'Authorization': 'Bearer secret'}
        )

    def test_quotes_history_raises_unauthorized_if_server_responds_with_401_status_code(self):
        schwab = SchwabUnauthorizedStub()

        with self.assertRaises(UnauthorizedError):
            schwab.price_history('aapl', '10daily', '1year')

    def test_price_history_raises_unauthorized_if_server_responds_with_401_status_code(self):
        schwab = SchwabUnauthorizedStub()

        with self.assertRaises(UnauthorizedError):
            schwab.price_history('aapl', '10daily', '1year')

    def test_price_history_raises_unabletoretrievestockdataerror_on_json_decoder_error(self):
        schwab = SchwabJsonDecoderErrorStub()

        with self.assertRaises(UnableToRetrieveStockDataError):
            schwab.price_history('aapl', '10daily', '1year')

    def test_quote_raises_unabletoretrievestockdataerror_on_json_decoder_error(self):
        schwab = SchwabJsonDecoderErrorStub()

        with self.assertRaises(UnableToRetrieveStockDataError):
            schwab.quotes(['aapl', '10daily'])

    @patch('stock_providers.schwab.requests')
    def test_price_history_refreshes_access_token_and_reruns_if_401_raised(self, mock_requests):
        mock_requests.configure_mock(**{
            'post.return_value.json.return_value': {
                'access_token': 'access-token',
                'refresh_token': 'refresh-token',
                'expires_in': '180'
            },
            'post.return_value.status_code': 200
        })

        schwab = SchwabReauthorizedStub()
        schwab.price_history('aapl', '10daily', '1year')

        mock_requests.post.assert_called_with(
            url='https://api.schwabapi.com/v1/oauth/token',
            headers={
                'Authorization': 'Basic a2V5OnNlY3JldA==',
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            data={'grant_type': 'refresh_token', 'refresh_token': 'secret'}
        )

        self.assertEqual(os.environ['SCHWAB_ACCESS_TOKEN'], 'access-token')
        self.assertEqual(os.environ['SCHWAB_REFRESH_TOKEN'], 'refresh-token')
        self.assertEqual(os.environ['SCHWAB_TOKEN_EXPIRES_IN'], '180')
        self.assertEqual(schwab._price_history_call_count, 2)
