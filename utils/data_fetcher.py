import yfinance as yf
import pandas as pd
import os
from datetime import datetime, timedelta
from config import Config

class DataFetcher:
    @staticmethod
    def get_stock_data(ticker):
        """Mengambil data saham dengan caching"""
        cache_path = os.path.join(Config.CACHE_DIR, f"{ticker}_hist.csv")
        
        # Cek cache
        if DataFetcher._is_cache_valid(cache_path):
            try:
                return DataFetcher._load_from_cache(cache_path)
            except:
                pass
        
        # Ambil data baru
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="1y", interval="1d")
            if not hist.empty:
                hist.index = hist.index.tz_localize(None)
                hist.to_csv(cache_path)
                return hist
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
        
        return pd.DataFrame()

    @staticmethod
    def _is_cache_valid(cache_path):
        if not os.path.exists(cache_path):
            return False
        file_time = datetime.fromtimestamp(os.path.getmtime(cache_path))
        return (datetime.now() - file_time) < timedelta(hours=Config.CACHE_TTL_HOURS)

    @staticmethod
    def _load_from_cache(cache_path):
        df = pd.read_csv(cache_path, index_col=0, parse_dates=True)
        df.index = df.index.tz_localize(None)
        return df
