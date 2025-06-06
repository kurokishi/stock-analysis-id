# utils/validator.py
import re
from datetime import datetime

class StockValidator:
    @staticmethod
    def validate_investment_amount(amount):
        """Validasi jumlah investasi minimal Rp100.000"""
        try:
            return float(amount) >= 100000
        except (ValueError, TypeError):
            return False

    @staticmethod
    def validate_ticker(ticker):
        """Validasi format ticker saham"""
        if not isinstance(ticker, str):
            return False
        if len(ticker) < 2:
            return False
        return ticker.isalnum()
        
    @staticmethod
    def filter_valid_tickers(tickers):
        """Filter ticker yang valid dengan format yang benar"""
        valid = []
        for t in tickers:
            try:
                t_clean = str(t).strip().upper()
                
                # Validasi format ticker (contoh: 'BBCA.JK' atau 'AAPL')
                if re.match(r'^[A-Z]{2,5}(\.[A-Z]{2})?$', t_clean):
                    valid.append(t_clean)
            except:
                continue
        return valid

    @staticmethod
    def validate_date_range(start_date, end_date):
        """Validasi range tanggal"""
        if start_date >= end_date:
            return False, "Tanggal mulai harus sebelum tanggal akhir"
        if end_date > datetime.now().date():
            return False, "Tanggal akhir tidak boleh di masa depan"
        return True, ""

    @staticmethod
    def validate_prediction_days(days):
        """Validasi hari prediksi"""
        return 1 <= days <= 365  # Between 1 day and 1 year

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
