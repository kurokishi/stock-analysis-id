import re
from datetime import datetime, timedelta
import pandas as pd

class StockValidator:
    @staticmethod
    def validate_ticker(ticker):
        """Validasi format ticker saham"""
        # Contoh: BBCA.JK, UNVR.JK, atau AAPL (untuk US stock)
        pattern = r'^[A-Z]{1,5}(\.[A-Z]{2})?$'
        return bool(re.match(pattern, ticker))

    @staticmethod
    def validate_date_range(start_date, end_date):
        """Validasi range tanggal"""
        if start_date >= end_date:
            return False, "Tanggal mulai harus sebelum tanggal akhir"
        if end_date > datetime.now().date():
            return False, "Tanggal akhir tidak boleh di masa depan"
        return True, ""

    @staticmethod
    def validate_investment_amount(amount):
        """Validasi jumlah investasi"""
        return amount >= 100000  # Minimal Rp100.000

    @staticmethod
    def validate_prediction_days(days):
        """Validasi hari prediksi"""
        return 1 <= days <= 365  # Between 1 day and 1 year

    @staticmethod
    def filter_valid_tickers(tickers):
        """Filter list ticker yang valid"""
        return [t for t in tickers if StockValidator.validate_ticker(t)]

    @staticmethod
    def validate_dataframe_for_analysis(df, min_days=30):
        """Validasi DataFrame untuk analisis"""
        if df.empty:
            return False, "Data kosong"
        if len(df) < min_days:
            return False, f"Data historis kurang dari {min_days} hari"
        if 'Close' not in df.columns:
            return False, "Kolom 'Close' tidak ditemukan"
        return True, ""
