from functools import reduce

# Generates a deterministic integer that is different for each symbol
differentiator = lambda symbol: reduce(lambda x, c: x + ord(c), list(symbol), 0)

def schwab_price_history_api_response_success(symbol='AAPL', price_history_length=2, empty=False):
    possible_candles = [
        {
            "open": 171.06 + differentiator(symbol),
            "high": 171.24 + differentiator(symbol),
            "low": 168.68 + differentiator(symbol),
            "close": 169.12 + differentiator(symbol),
            "volume": 68587707 + differentiator(symbol),
            "datetime": 1709704800000 + differentiator(symbol)
        },
        {
            "open": 169.15 + differentiator(symbol),
            "high": 170.73 + differentiator(symbol),
            "low": 168.49 + differentiator(symbol),
            "close": 169.0 + differentiator(symbol),
            "volume": 71765061 + differentiator(symbol),
            "datetime": 1709791200000 + differentiator(symbol)
        },
    ]

    return_candles = possible_candles[:price_history_length]

    return {
        "candles": return_candles,
        "symbol": symbol,
        "empty": empty
    }

def schwab_quotes_api_response_success(symbols=['META', 'AAPL'], **kwargs):
    return {
       symbol.upper(): {
            "assetMainType": "EQUITY",
            "assetSubType": "COE",
            "quoteType": "NBBO",
            "realtime": True,
            "ssid": 1831567943 + differentiator(symbol),
            "symbol": symbol.upper(),
            "fundamental": {
                "avg10DaysVolume": 1.1555512E7,
                "avg1YearVolume": 1.9318454E7,
                "declarationDate": "2024-05-30T04:00:00Z",
                "divAmount": 2.0,
                "divExDate": "2024-06-14T04:00:00Z",
                "divFreq": 4,
                "divPayAmount": 0.5,
                "divPayDate": "2024-06-26T04:00:00Z",
                "divYield": 0.40506,
                "eps": 14.87,
                "fundLeverageFactor": 0.0,
                "lastEarningsDate": "2024-04-24T04:00:00Z",
                "nextDivExDate": "2024-09-16T04:00:00Z",
                "nextDivPayDate": "2024-09-26T04:00:00Z",
                "peRatio": 28.40842
            },
            "quote": {
                "52WeekHigh": 531.49,
                "52WeekLow": 258.88,
                "askMICId": "ARCX",
                "askPrice": 492.9,
                "askSize": 5,
                "askTime": 1717804788964,
                "bidMICId": "ARCX",
                "bidPrice": 492.25,
                "bidSize": 4,
                "bidTime": 1717804788964,
                "closePrice": 493.76 + differentiator(symbol),
                "highPrice": 498.91 + differentiator(symbol),
                "lastMICId": "XADF",
                "lastPrice": 492.575 + differentiator(symbol),
                "lastSize": 1,
                "lowPrice": 490.1701 + differentiator(symbol),
                "mark": 492.96,
                "markChange": -0.8,
                "markPercentChange": -0.16202203,
                "netChange": -1.185,
                "netPercentChange": -0.23999514,
                "openPrice": 495.91 + differentiator(symbol),
                "postMarketChange": -0.385,
                "postMarketPercentChange": -0.07809964,
                "quoteTime": kwargs["quote_time"] if kwargs.get("quote_time") else 1717804788964 + differentiator(symbol),
                "securityStatus": "Normal",
                "totalVolume": 9380745,
                "tradeTime": 1717804795237 + differentiator(symbol)
            },
            "reference": {
                "cusip": "30303M102",
                "description": "META PLATFORMS INC A",
                "exchange": "Q",
                "exchangeName": "NASDAQ",
                "isHardToBorrow": False,
                "isShortable": True,
                "htbRate": 0.0
            },
            "regular": {
                "regularMarketLastPrice": 492.96,
                "regularMarketLastSize": 735688,
                "regularMarketNetChange": -0.8,
                "regularMarketPercentChange": -0.16202203,
                "regularMarketTradeTime": 1717790400677
            }
        }
        for symbol in symbols
    }