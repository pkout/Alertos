"""Wrapper for Polygon.io stock API."""

import os
import re
import requests

from core import config

class Schwab:
    """
    Schwab trader API wrapper. See this URL documentation:
    https://developer.schwab.com/products/trader-api--individual/details/specifications/Market%20Data%20Production
    """

    PRICE_HISTORY_API_URL_PATTERN = ''.join([
        'https://api.schwabapi.com/marketdata/v1/pricehistory?symbol={0}&',
        'periodType={1}&period={2}&frequencyType={3}&frequency={4}'
    ])

    min_api_requests_interval_secs = config.Schwab.MinApiRequestsIntervalSecs

    def __init__(self):
        self._api_key = os.environ['SCHWAB_API_KEY']
        self._api_secret = os.environ['SCHWAB_API_SECRET']
        self._access_token = os.environ['SCHWAB_ACCESS_TOKEN']
        self._refresh_token = None

    def access_token_from_refresh_token(self):
        """Requests a new access token using the refresh token."""
        pass

    def price_history(self, symbol, frequency, period, start_date=None,
                      end_date=None, include_extended_data=False):
        """Returns the ticker symbol market data for the given parameters.

        @param: symbol The ticker symbol string
        @param: frequency The frequency (e.g. 1minute, 5minute, 1daily)
        @param: period The period (e.g. 4month, 5day)
        @param: start_date The date of the start of data in epoch (1451624400000)
        @param: end_date The date of the end of data in epoch (1451624400000)
        @param: include_extended_data Bool
        @return: dict

        The `start_date` and `end_date` arguments are optional.

        Valid values for frequency are:
            If the period unit is
                • day - valid value is minute
                • month - valid values are daily, weekly
                • year - valid values are daily, weekly, monthly
                • ytd - valid values are daily, weekly

        Valid values for period are:
            • 1day, 2day, 3day, 4day, 5day, 10day
            • 1month, 2month, 3month, 6month
            • 1year, 2year, 3year, 5year, 10year, 15year, 20year
            • 1ytd
        """
        freq_multiplier, freq_unit = \
            self._frequency_to_multiplier_and_unit(frequency)

        period_multiplier, period_unit = \
            self._period_to_multiplier_and_unit(period)

        url = Schwab.PRICE_HISTORY_API_URL_PATTERN.format(
            symbol.upper(),
            period_multiplier,
            period_unit,
            freq_multiplier,
            freq_unit
        )

        if start_date is not None:
            url += f'&startDate={start_date}'

        if end_date is not None:
            url += f'&endDate={end_date}'

        if include_extended_data is not None:
            value = 'true' if include_extended_data else 'false'
            url += f'&needExtendedData={value}'

        url += '&needPreviousClose=true'

        response = requests.get(url, timeout=5)

        symbol_data_dict = response.json()

        return symbol_data_dict

    def _frequency_to_multiplier_and_unit(self, frequency):
        split = re.split('(\d+)', frequency)
        split = list(filter(None, split)) # Remove the '' as the first item

        return split

    def _period_to_multiplier_and_unit(self, period):
        split = re.split('(\d+)', period)
        split = list(filter(None, split)) # Remove the '' as the first item

        return split