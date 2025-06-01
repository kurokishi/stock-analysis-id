import os
import pandas as pd
from datetime import datetime, timedelta
import yfinance as yf
from models.stock import StockData, StockInfo

class StockDataProvider:
    def __init__(self, cache_dir="cache", ttl_hours=1):
        self.cache_dir = cache_dir
        self.ttl = timedelta(hours=ttl_hours)
        
    def _is_cache_valid(self, path):
        if not os.path.exists(path):
            return False
        mod_time = datetime.fromtimestamp(os.path.getmtime(path))
        return (datetime.now() - mod_time) < self.ttl
        
    def get_stock_data(self, ticker) -> StockData:
        os.makedirs(self.cache_dir, exist_ok=True)
        cache_path = os.path.join(self.cache_dir, f"{ticker}_hist.csv")
        
        if self._is_cache_valid(cache_path):
            try:
                df = pd.read_csv(cache_path, index_col=0, parse_dates=True)
                df.index = df.index.tz_localize(None)
                return StockData(
                    ticker=ticker,
                    dates=df.index.to_list(),
                    opens=df['Open'].to_list(),
                    highs=df['High'].to_list(),
                    lows=df['Low'].to_list(),
                    closes=df['Close'].to_list(),
                    volumes=df['Volume'].to_list()
                )
            except Exception:
                pass
        
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="1y", interval="1d")
            if not hist.empty:
                hist.index = hist.index.tz_localize(None)
                hist.to_csv(cache_path)
                return StockData(
                    ticker=ticker,
                    dates=hist.index.to_list(),
                    opens=hist['Open'].to_list(),
                    highs=hist['High'].to_list(),
                    lows=hist['Low'].to_list(),
                    closes=hist['Close'].to_list(),
                    volumes=hist['Volume'].to_list()
                )
        except Exception:
            pass
            
        return StockData(ticker, [], [], [], [], [], [])

    def get_stock_info(self, ticker) -> StockInfo:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            return StockInfo(
                ticker=ticker,
                name=info.get('longName', 'N/A'),
                sector=info.get('sector', 'N/A'),
                industry=info.get('industry', 'N/A'),
                country=info.get('country', 'N/A'),
                currency=info.get('currency', 'IDR'),
                market_cap=info.get('marketCap', 0),
                pe_ratio=info.get('trailingPE', None),
                pb_ratio=info.get('priceToBook', None),
                dividend_yield=info.get('dividendYield', None)
            )
        except Exception:
            return StockInfo(ticker, 'N/A', 'N/A', 'N/A', 'N/A', 'IDR', 0, None, None, None)
