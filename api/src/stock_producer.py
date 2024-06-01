"""
Serves stocks ticker data from an external source (Polygon.io) by
publishing them to a Redis pubsub queue.

Which stocks get loaded is determined by the need of existing
alerts in the database.
"""

import signal
import sys
import time

from mongoengine import connect

from core.config import Config, Environment
from core.utils import ExtendedEnum
from stock_providers.stock_provider_polygon import Polygon
from stock_subscriptions_details_sources.stock_subscriptions_details_source_alerts import Alerts

shutdown = False

def signal_handler(sig, frame):
    print('Gracefully shutting down')
    global shutdown
    shutdown = True

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

config = Config(Environment.DEV.value).to_dotdict()

connection = connect(host=config.Database.ConnectionString,
                     db=config.Database.Name)

class StockDataProvider(ExtendedEnum):
    POLYGON = 'Polygon'

class StockSubscriptionsDetailsSource(ExtendedEnum):
    ALERTS = 'alerts'

class UnknownStockProviderError(Exception):
    """Returned when the stock provider is unknown."""

class UnknownStockSubscriptionsDetailsSourceError(Exception):
    """Returned when the stock subscriptions details source is unknown."""

class StockProviderFactory:

    def build(self):
        if config.Stocks.Provider == StockDataProvider.POLYGON.value:
            return Polygon()

        raise UnknownStockProviderError(f'Provider: {config.Stocks.Provider}')

class StockSubscriptionsDetailsSourceFactory:

    def build(self):
        if config.Stocks.SubscriptionsDetailsSource == StockSubscriptionsDetailsSource.ALERTS.value:
            return Alerts()

        raise UnknownStockSubscriptionsDetailsSourceError(
            f'Source: {config.Stocks.SubscriptionsDetailsSource}'
        )

def produce(stock_provider, stock_subscriptions_details_source):
    subscriptions = stock_subscriptions_details_source.list_subscriptions()

    while True:
        if shutdown:
            sys.exit()

        for s in subscriptions:
            print(s)

        time.sleep(3)


if __name__ == '__main__':
    stock_provider = StockProviderFactory().build()
    stock_subscription_details_source = StockSubscriptionsDetailsSourceFactory().build()

    produce(stock_provider, stock_subscription_details_source)
