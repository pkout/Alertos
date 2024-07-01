from unittest.mock import Mock, create_autospec
from test_stock_providers.fixtures import api_fixtures
from stock_providers.schwab import Schwab
from stock_providers.schwab import authorized

from stock_providers.exceptions import UnauthorizedError
from stock_providers.exceptions import UnableToRetrieveStockDataError

class SchwabStub(Schwab):

    def __init__(self, price_history_length=2):
        self._price_history_length = price_history_length

    def price_history(self, symbol, frequency, period, start_date=None,
                      end_date=None, include_extended_data=False):
        return api_fixtures.schwab_price_history_api_response_success(
            symbol,
            self._price_history_length
        )

    def quotes(self, symbols):
        return api_fixtures.schwab_quotes_api_response_success(symbols)

class SchwabQuoteUpdate2SecondsAfterPriceHistoryCandleStub(Schwab):

    def __init__(self, price_history_length=2):
        self._price_history_length = price_history_length

    def price_history(self, symbol, frequency, period, start_date=None,
                      end_date=None, include_extended_data=False):
        data = api_fixtures.schwab_price_history_api_response_success(
            symbol,
            self._price_history_length
        )

        data['candles'][-1]['datetime'] = 1709791200414

        return data

    def quotes(self, symbols):
        return api_fixtures.schwab_quotes_api_response_success(
            symbols,
            quote_time=1709791220414 # 2 seconds after last price history candle
        )

class SchwabQuoteUpdate60SecondsAfterPriceHistoryCandleStub(Schwab):

    def __init__(self, price_history_length=2):
        self._price_history_length = price_history_length

    def price_history(self, symbol, frequency, period, start_date=None,
                      end_date=None, include_extended_data=False):
        data = api_fixtures.schwab_price_history_api_response_success(
            symbol,
            self._price_history_length
        )

        data['candles'][-1]['datetime'] = 1709791200414

        return data

    def quotes(self, symbols):
        return api_fixtures.schwab_quotes_api_response_success(
            symbols,
            quote_time=1709791260414 # 60 seconds after last price history candle
        )

class SchwabQuoteUpdateWithin1MinuteAndAfter1DayStub(Schwab):

    def __init__(self, price_history_length=2):
        self._quotes_call_count = 0
        self._price_history_length = price_history_length

    def price_history(self, symbol, frequency, period, start_date=None,
                      end_date=None, include_extended_data=False):
        return api_fixtures.schwab_price_history_api_response_success(
            symbol,
            self._price_history_length
        )

    def quotes(self, symbols):
        self._quotes_call_count += 1

        if self._quotes_call_count == 1:
            return api_fixtures.schwab_quotes_api_response_success(
                symbols,
                quoteTime=1718083998000
            )

        return api_fixtures.schwab_quotes_api_response_success(
            symbols,
            quoteTime=1718160502000
        )

class SchwabUnauthorizedStub(Schwab):

    def __init__(self):
        pass

    def price_history(self, symbol, frequency, period, start_date=None,
                      end_date=None, include_extended_data=False):
        raise UnauthorizedError()

class SchwabJsonDecoderErrorStub(Schwab):

    def __init__(self):
        self._price_history_call_count = 0
        self._price_history_success_call_count = 0

    def price_history(self, symbol, frequency, period, start_date=None,
                      end_date=None, include_extended_data=False):
        self._price_history_call_count += 1

        if self._price_history_call_count == 1:
            raise UnableToRetrieveStockDataError('my error')
        else:
            self._price_history_success_call_count += 1

            return api_fixtures.schwab_price_history_api_response_success(
                symbol,
                1
            )

    def quotes(self, symbols):
        raise UnableToRetrieveStockDataError('my error')

class SchwabReauthorizedStub(Schwab):

    def __init__(self):
        self._price_history_call_count = 0

    @authorized
    def price_history(self, symbol, frequency, period, start_date=None,
                      end_date=None, include_extended_data=False):
        self._price_history_call_count += 1

        if self._price_history_call_count < 2:
            raise UnauthorizedError()