# utils/validator.py
import re
from datetime import datetime

class StockValidator:
    @staticmethod
    def filter_valid_tickers(tickers):
        # Implementasi logika validasi ticker di sini
        # Contoh sederhana:
        valid_tickers = [t for t in tickers if t and isinstance(t, str)]
        return valid_tickers

    @staticmethod
    def validate_date_range(start_date, end_date):
        """Validasi range tanggal"""
        if start_date >= end_date:
            return False, "Tanggal mulai harus sebelum tanggal akhir"
        if end_date > datetime.now().date():
            return False, "Tanggal akhir tidak boleh di masa depan"
        return True, ""

# Fungsi tambahan jika diperlukan
def validate_investment_amount(amount):
    return amount >= 100000

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
