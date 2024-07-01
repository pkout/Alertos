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
from test_stock_subscriptions_sources.doubles.alerts import AlertsStub
from test_stock_subscriptions_sources.doubles.alerts import OneMinuteSubscriptionAlertsStub
from test_stock_providers.fixtures import api_fixtures
from test_stock_providers.doubles.schwab import SchwabStub, SchwabQuoteUpdate2SecondsAfterPriceHistoryCandleStub
from test_stock_providers.doubles.schwab import SchwabStub, SchwabQuoteUpdate60SecondsAfterPriceHistoryCandleStub
from test_stock_providers.doubles.schwab import SchwabQuoteUpdateWithin1MinuteAndAfter1DayStub
from test_stock_providers.doubles.schwab import SchwabUnauthorizedStub
from test_stock_providers.doubles.schwab import SchwabJsonDecoderErrorStub

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
    def test_build_returns_schwab_stock_provider_instance(self):
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
        stock_data_provider_stub = SchwabStub()
        stock_subscriptions_source_stub = AlertsStub()
        stock_producer = StockProducer(stock_data_provider_stub, stock_subscriptions_source_stub)
        stock_producer.shutdown = True  # to exit the infinite while loop

        feed = stock_producer.subscriptions_data_feed(0.1)
        feed_item = next(feed)

        self.assertEqual(feed_item[0], ('aapl', '1minute', '1day'))

        self.assertEqual(
            json.loads(feed_item[1]),
            {
                "candles": [
                    {"open": 585.06, "high": 585.24, "low": 582.6800000000001, "close": 583.12, "volume": 68588121, "datetime": 1709704800414},
                    {"open": 583.15, "high": 584.73, "low": 582.49, "close": 583.0, "volume": 71765475, "datetime": 1709791200414}
                ],
                "symbol": "aapl",
                "empty": False
            }
        )

        feed_item = next(feed)

        self.assertEqual(feed_item[0], ('msft', '5minute', '10day'))

        self.assertEqual(
            json.loads(feed_item[1]),
            {
                "candles": [
                    {"open": 613.06, "high": 613.24, "low": 610.6800000000001, "close": 611.12, "volume": 68588149, "datetime": 1709704800442},
                    {"open": 611.15, "high": 612.73, "low": 610.49, "close": 611.0, "volume": 71765503, "datetime": 1709791200442}
                ],
                "symbol": "msft",
                "empty": False
            }
        )

    def test_subscriptions_data_feed_returns_last_price_with_timestamp_set_to_one_frequency_ahead_if_quote_update_arrived_within_frequency_step(self):
        stock_data_provider_stub = SchwabQuoteUpdate2SecondsAfterPriceHistoryCandleStub()
        stock_subscriptions_source_stub = OneMinuteSubscriptionAlertsStub()
        stock_producer = StockProducer(stock_data_provider_stub, stock_subscriptions_source_stub)

        feed = stock_producer.subscriptions_data_feed(0.1)
        feed_item = next(feed) # price history for AAPL
        # last_price_history_symbol_datetime = json.loads(feed_item[1])['candles'][-1]['datetime']
        feed_item = next(feed) # last price quote

        self.assertDictEqual(
            json.loads(feed_item[1]),
            {
                "52WeekHigh": 531.49, "52WeekLow": 258.88, "askMICId": "ARCX", "askPrice": 492.9,
                "askSize": 5, "askTime": 1717804788964, "bidMICId": "ARCX", "bidPrice": 492.25,
                "bidSize": 4, "bidTime": 1717804788964, "closePrice": 907.76,
                "highPrice": 912.9100000000001, "lastMICId": "XADF", "lastPrice": 906.575,
                "lastSize": 1, "lowPrice": 904.1701, "mark": 492.96, "markChange": -0.8,
                "markPercentChange": -0.16202203, "netChange": -1.185, "netPercentChange": -0.23999514,
                "openPrice": 909.9100000000001, "postMarketChange": -0.385,
                "postMarketPercentChange": -0.07809964, "quoteTime": 1709791260414,
                "securityStatus": "Normal", "totalVolume": 9380745, "tradeTime": 1717804795651
            }
        )

    def test_subscriptions_data_feed_returns_last_price_with_timestamp_set_to_two_frequencies_ahead_if_quote_arrived_after_frequency_step(self):
        stock_data_provider_stub = SchwabQuoteUpdate60SecondsAfterPriceHistoryCandleStub()
        stock_subscriptions_source_stub = OneMinuteSubscriptionAlertsStub()
        stock_producer = StockProducer(stock_data_provider_stub, stock_subscriptions_source_stub)

        feed = stock_producer.subscriptions_data_feed(0.1)
        feed_item = next(feed) # price history for AAPL
        feed_item = next(feed) # last price quote

        self.assertDictEqual(
            json.loads(feed_item[1]),
            {
                "52WeekHigh": 531.49, "52WeekLow": 258.88, "askMICId": "ARCX", "askPrice": 492.9,
                "askSize": 5, "askTime": 1717804788964, "bidMICId": "ARCX", "bidPrice": 492.25,
                "bidSize": 4, "bidTime": 1717804788964, "closePrice": 907.76,
                "highPrice": 912.9100000000001, "lastMICId": "XADF", "lastPrice": 906.575,
                "lastSize": 1, "lowPrice": 904.1701, "mark": 492.96, "markChange": -0.8,
                "markPercentChange": -0.16202203, "netChange": -1.185, "netPercentChange": -0.23999514,
                "openPrice": 909.9100000000001, "postMarketChange": -0.385,
                "postMarketPercentChange": -0.07809964, "quoteTime": 1709791320414,
                "securityStatus": "Normal", "totalVolume": 9380745, "tradeTime": 1717804795651
            }
        )

    def test_subscriptions_data_feed_skips_feed_iteration_if_unabletoretrievestockdataerror_raised(self):
        stock_data_provider_stub = SchwabJsonDecoderErrorStub()
        stock_subscriptions_source_stub = OneMinuteSubscriptionAlertsStub()
        stock_producer = StockProducer(stock_data_provider_stub, stock_subscriptions_source_stub)

        feed = stock_producer.subscriptions_data_feed(0.1)
        next(feed)

        # The first call ended in the exception handler, the second call returned expected data.
        self.assertTrue(stock_data_provider_stub._price_history_success_call_count, 1)