"""
Serves stocks ticker data from an external source (Schwab) by
publishing them to a Redis pubsub queue.

Which stocks get loaded is determined by the need of existing
alerts in the database.
"""

import datetime
import json
import redis
import signal
import time
import traceback

from mongoengine import connect

from core.utils import ExtendedEnum
from core.logging import get_logger
from core import config
from stock_providers.schwab import Schwab
from stock_providers.exceptions import UnableToRetrieveStockDataError
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
        self._price_history = {}
        self._unclosed_candles_close_timestamps = {}

    def subscriptions_data_feed(self, update_interval_secs):
        """Returns a generator iterating through tuples of
        (subscription, market data) for all subscriptions defined
        in configuration.
        """
        while True:
            subscriptions = self._stock_subscriptions_source.list_subscriptions()
            symbols = [s[0] for s in subscriptions]
            self._log_subscriptions(subscriptions)

            if self._price_history == {}:
                try:
                    for subscription in subscriptions:
                        yield self._load_price_history_for(subscription)
                except UnableToRetrieveStockDataError:
                    logger.error(traceback.format_exc())
                    continue

            self._calc_unclosed_candles_close_timestamps()

            time.sleep(update_interval_secs)

            try:
                quotes_ohlcv = self._stock_data_provider.quotes(symbols)
            except UnableToRetrieveStockDataError:
                logger.error(traceback.format_exc())
                continue

            for subscription in subscriptions:
                quote_ohlcv = self._upsert_unclosed_candle_timestamp(
                    subscription,
                    quotes_ohlcv
                )

                yield subscription, json.dumps(quote_ohlcv)

            if self.shutdown:
                return

    def _load_price_history_for(self, subscription):
        symbol, frequency, period = subscription

        price_history_ohlcv = self._stock_data_provider.price_history(
            symbol=symbol,
            frequency=frequency,
            period=period,
            end_date=int(datetime.datetime.now().timestamp() * 1000)
        )

        self._price_history[subscription] = price_history_ohlcv

        return subscription, json.dumps(self._price_history[subscription])

    def _calc_unclosed_candles_close_timestamps(self):
        for subscription, ph in self._price_history.items():
            last_candle_timestamp = ph['candles'][-1]['datetime']
            self._unclosed_candles_close_timestamps[subscription] = last_candle_timestamp + 60000

    def _upsert_unclosed_candle_timestamp(self, subscription, quotes_ohlcv):
        symbol = subscription[0]
        quote_ohlcv = quotes_ohlcv[symbol.upper()]['quote']
        quote_timestamp = quote_ohlcv['quoteTime']

        if (self._unclosed_candles_close_timestamps[subscription] - quote_timestamp) <= 0:  # Replace with frequency
            self._unclosed_candles_close_timestamps[subscription] += 60000

        quote_ohlcv['quoteTime'] = self._unclosed_candles_close_timestamps[subscription]

        return quote_ohlcv


    def produce(self, subscriptions_data_feed):
        """Pushes the subscriptions and their market data to
        a Redis channel.
        """
        for subscription, stock_ohlcv in subscriptions_data_feed:
            retries = 3

            try:
                symbol, frequency, period = subscription
                channel_name = f'symbol-{symbol}-{frequency}-{period}'
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
            config.Schwab.MarketDataUpdateIntervalSecs
        )
    )
