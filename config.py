import os

class Config:
    CACHE_DIR = "cache"
    CACHE_TTL_HOURS = 1
    DEFAULT_TICKERS = ["UNVR.JK", "BBCA.JK", "TLKM.JK"]
    
    @staticmethod
    def setup():
        os.makedirs(Config.CACHE_DIR, exist_ok=True)
