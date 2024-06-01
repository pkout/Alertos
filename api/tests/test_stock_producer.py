import unittest
from unittest.mock import patch

from core.utils import DotDict
from stock_producer import StockProviderFactory
from stock_producer import UnknownStockProviderError
from stock_producer import StockSubscriptionsDetailsSourceFactory
from stock_producer import UnknownStockSubscriptionsDetailsSourceError
from stock_providers.stock_provider_polygon import Polygon
from stock_subscriptions_details_sources.stock_subscriptions_details_source_alerts import Alerts

class TestStockProducer_StockProviderFactory(unittest.TestCase):

    @patch('stock_producer.config', DotDict({'Stocks': {'Provider': 'Polygon'}}))
    def test_build_returns_polygon_stock_provider_instance(self):
        factory = StockProviderFactory()
        stock_provider = factory.build()
        self.assertIsInstance(stock_provider, Polygon)

    @patch('stock_producer.config', DotDict({'Stocks': {'Provider': 'Unknown'}}))
    def test_build_raises_if_stock_provider_unknown(self):
        factory = StockProviderFactory()

        with self.assertRaises(UnknownStockProviderError):
            factory.build()

class TestStockProducer_StockSubscriptionsDetailsSourceFactory(unittest.TestCase):

    @patch('stock_producer.config', DotDict({'Stocks': {'SubscriptionsDetailsSource': 'alerts'}}))
    def test_build_returns_alerts_model(self):
        factory = StockSubscriptionsDetailsSourceFactory()
        subscriptions_provider = factory.build()
        self.assertIsInstance(subscriptions_provider, Alerts)

    @patch('stock_producer.config', DotDict({'Stocks': {'SubscriptionsDetailsSource': 'unknown'}}))
    def test_build_raises_if_stock_subscription_details_source_unknown(self):
        factory = StockSubscriptionsDetailsSourceFactory()

        with self.assertRaises(UnknownStockSubscriptionsDetailsSourceError):
            factory.build()