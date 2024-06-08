"""
Serves stocks ticker data from an external source (Schwab) by
publishing them to a Redis pubsub queue.

Which stocks get loaded is determined by the need of existing
alerts in the database.
"""

import json
import redis
import signal
import time

from mongoengine import connect

from core.utils import ExtendedEnum
from core.logging import get_logger
from core import config
from stock_providers.schwab import Schwab
from stock_subscriptions_sources.alerts import Alerts

redis_client = redis.Redis(host='redis', port=6379)

shutdown = False

logger = get_logger(__name__)

connection = connect(host=config.Database.ConnectionString,
                     db=config.Database.Name)

class StockDataProvider(ExtendedEnum):
    SCHWAB = 'Schwab'

class StockSubscriptionsSource(ExtendedEnum):
    ALERTS = 'alerts'

class UnknownStockProviderError(Exception):
    """Returned when the stock provider is unknown."""

class UnknownStockSubscriptionsSourceError(Exception):
    """Returned when the stock subscriptions source is unknown."""

class StockProviderFactory:

    def build(self):
        if config.Stocks.Provider == StockDataProvider.SCHWAB.value:
            return Schwab()

        raise UnknownStockProviderError(f'Provider: {config.Stocks.Provider}')

class StockSubscriptionsSourceFactory:

    def build(self):
        if config.Stocks.SubscriptionsSource == StockSubscriptionsSource.ALERTS.value:
            return Alerts()

        raise UnknownStockSubscriptionsSourceError(
            f'Source: {config.Stocks.SubscriptionsSource}'
        )

class StockProducer:

    def __init__(self, stock_data_provider, stock_subscriptions_source):
        self.shutdown = False
        self._stock_data_provider = stock_data_provider
        self._stock_subscriptions_source = stock_subscriptions_source

    def subscriptions_data_feed(self, pause_between_requests_secs):
        """Returns a generator iterating through tuples of
        (subscription, market data) for all subscriptions defined
        in configuration.
        """
        while True:
            subscriptions = self._stock_subscriptions_source.list_subscriptions()
            self._log_subscriptions(subscriptions)

            for subscription in subscriptions:
                symbol, frequency, period = subscription

                stock_ohlcv = self._stock_data_provider.price_history(
                    symbol,
                    frequency,
                    period
                )

                yield subscription, json.dumps(stock_ohlcv)

            if self.shutdown:
                return

            time.sleep(pause_between_requests_secs)

    def produce(self, subscriptions_data_feed):
        """Pushes the subscriptions and their market data to
        a Redis channel.
        """
        for subscription, stock_ohlcv in subscriptions_data_feed:
            retries = 3

            try:
                symbol, frequency = subscription
                channel_name = f'symbol-{symbol}-{frequency}'
                redis_client.publish(channel_name, json.dumps(stock_ohlcv))
                logger.info(f'Published ticker symbol data to channel: {channel_name}')
            except redis.exceptions.ConnectionError as exc:
                if retries == 0:
                    raise exc

                retries -= 1
                time.sleep(0.5)

    def _log_subscriptions(self, subscriptions):
        logger.info('Subscriptions:')
        list(map(lambda s: logger.info(f'\t{s[0]}, {s[1]}'), subscriptions))


if __name__ == '__main__':
    stock_provider = StockProviderFactory().build()
    stock_subscription_source = StockSubscriptionsSourceFactory().build()
    stock_producer = StockProducer(stock_provider, stock_subscription_source)

    def signal_handler(sig, frame):
        logger.info('Gracefully shutting down')
        stock_producer.shutdown = True

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    stock_producer.produce(
        stock_producer.subscriptions_data_feed(
            stock_provider.min_api_requests_interval_secs
        )
    )
