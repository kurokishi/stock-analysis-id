import pandas as pd
import numpy as np
from models.stock import StockData, StockInfo  # Tambahkan ini
from models.prediction import PredictionResult

class FundamentalAnalyzer:
    @staticmethod
    def analyze_financials(stock_info: StockInfo):
        # Implementasi analisis fundamental
        pass
# Tambahkan impor StockInfo di bagian atas file
class TechnicalAnalyzer:
    @staticmethod
    def calculate_rsi(prices, window=14):
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    @staticmethod
    def calculate_macd(prices, slow=26, fast=12, signal=9):
        exp1 = prices.ewm(span=fast, adjust=False).mean()
        exp2 = prices.ewm(span=slow, adjust=False).mean()
        macd = exp1 - exp2
        signal_line = macd.ewm(span=signal, adjust=False).mean()
        return macd, signal_line

    @staticmethod
    def add_technical_indicators(stock_data: StockData) -> StockData:
        df = stock_data.to_dataframe()
        
        # Moving Averages
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        df['SMA_50'] = df['Close'].rolling(window=50).mean()
        
        # RSI
        df['RSI'] = TechnicalAnalyzer.calculate_rsi(df['Close'])
        
        # MACD
        macd, signal = TechnicalAnalyzer.calculate_macd(df['Close'])
        df['MACD'] = macd
        df['Signal'] = signal
        
        # Update stock data
        return StockData(
            ticker=stock_data.ticker,
            dates=df.index.to_list(),
            opens=df['Open'].to_list(),
            highs=df['High'].to_list(),
            lows=df['Low'].to_list(),
            closes=df['Close'].to_list(),
            volumes=df['Volume'].to_list()
        )
