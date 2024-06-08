def schwab_price_history_api_response_success(symbol='AAPL', empty=False):
    return {
        "candles": [
            {
                "open": 171.06,
                "high": 171.24,
                "low": 168.68,
                "close": 169.12,
                "volume": 68587707,
                "datetime": 1709704800000
            },
            {
                "open": 169.15,
                "high": 170.73,
                "low": 168.49,
                "close": 169.0,
                "volume": 71765061,
                "datetime": 1709791200000
            },
        ],
        "symbol": symbol,
        "empty": empty
    }