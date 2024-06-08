# pylint:disable=missing-module-docstring, missing-class-docstring
# pylint:disable=missing-function-docstring, invalid-name, line-too-long

import json
import os
import unittest
from unittest.mock import create_autospec, patch

from core.utils import DotDict
from stock_producer import StockProviderFactory
from stock_producer import UnknownStockProviderError
from stock_producer import StockProducer
from stock_producer import StockSubscriptionsSourceFactory
from stock_producer import UnknownStockSubscriptionsSourceError
from stock_providers.schwab import Schwab
from stock_subscriptions_sources.alerts import Alerts
from test_stock_providers.fixtures import api_fixtures

class Test_StockProducer_StockProviderFactory(unittest.TestCase):

    def setUp(self):
        os.environ['SCHWAB_API_KEY'] = 'key'
        os.environ['SCHWAB_API_SECRET'] = 'secret'
        os.environ['SCHWAB_ACCESS_TOKEN'] = 'secret'

    def tearDown(self):
        del os.environ['SCHWAB_API_KEY']
        del os.environ['SCHWAB_API_SECRET']
        del os.environ['SCHWAB_ACCESS_TOKEN']

    @patch('stock_producer.config', DotDict({'Stocks': {'Provider': 'Schwab'}}))
    def test_build_returns_polygon_stock_provider_instance(self):
        factory = StockProviderFactory()
        stock_provider = factory.build()
        self.assertIsInstance(stock_provider, Schwab)

    @patch('stock_producer.config', DotDict({'Stocks': {'Provider': 'Unknown'}}))
    def test_build_raises_if_stock_provider_unknown(self):
        factory = StockProviderFactory()

        with self.assertRaises(UnknownStockProviderError):
            factory.build()

class Test_StockProducer_StockSubscriptionsSourceFactory(unittest.TestCase):

    def setUp(self):
        os.environ['SCHWAB_API_KEY'] = 'key'
        os.environ['SCHWAB_API_SECRET'] = 'secret'
        os.environ['SCHWAB_ACCESS_TOKEN'] = 'secret'

    def tearDown(self):
        del os.environ['SCHWAB_API_KEY']
        del os.environ['SCHWAB_API_SECRET']
        del os.environ['SCHWAB_ACCESS_TOKEN']

    @patch('stock_producer.config', DotDict({'Stocks': {'SubscriptionsSource': 'alerts'}}))
    def test_build_returns_alerts_model(self):
        factory = StockSubscriptionsSourceFactory()
        subscriptions_provider = factory.build()
        self.assertIsInstance(subscriptions_provider, Alerts)

    @patch('stock_producer.config', DotDict({'Stocks': {'SubscriptionsSource': 'unknown'}}))
    def test_build_raises_if_stock_subscription_details_source_unknown(self):
        factory = StockSubscriptionsSourceFactory()

        with self.assertRaises(UnknownStockSubscriptionsSourceError):
            factory.build()

class Test_StockProducer_StockProducer(unittest.TestCase):

    def test_subscriptions_data_feed_returns_generator_of_2_subscriptions_and_their_market_data(self):
        stock_data_provider = create_autospec(Schwab)
        stub_stock_provider_price_history_payloads = [ # two consecutive calls because two subscriptions
            api_fixtures.schwab_price_history_api_response_success('AAPL'),
            api_fixtures.schwab_price_history_api_response_success('MSFT')
        ]
        stock_data_provider.price_history.side_effect = stub_stock_provider_price_history_payloads
        stock_subscriptions_source = create_autospec(Alerts)
        stub_subscriptions = [('aapl', '4daily', '6month'), ('msft', '5minute', '6month')]
        stock_subscriptions_source.list_subscriptions.return_value = stub_subscriptions
        stock_producer = StockProducer(stock_data_provider, stock_subscriptions_source)
        stock_producer.shutdown = True  # to exit the infinite while loop

        result = stock_producer.subscriptions_data_feed(0.1)

        for i, r in enumerate(result):
            self.assertEqual(r[0], stub_subscriptions[i])
            self.assertEqual(r[1], json.dumps(stub_stock_provider_price_history_payloads[i]))

    def test_subscriptions_data_feed_passes_correct_arguments_to_price_history_method(self):
        stock_data_provider = create_autospec(Schwab)
        stub_stock_provider_price_history_payloads = [
            api_fixtures.schwab_price_history_api_response_success('AAPL'),
        ]
        stock_data_provider.price_history.side_effect = stub_stock_provider_price_history_payloads
        stock_subscriptions_source = create_autospec(Alerts)
        stub_subscriptions = [('aapl', '4daily', '6month')]
        stock_subscriptions_source.list_subscriptions.return_value = stub_subscriptions
        stock_producer = StockProducer(stock_data_provider, stock_subscriptions_source)
        stock_producer.shutdown = True  # to exit the infinite while loop

        list(stock_producer.subscriptions_data_feed(0.1))

        stock_data_provider.price_history.assert_called_with(
            'aapl', '4daily', '6month'
        )