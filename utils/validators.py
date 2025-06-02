from datetime import datetime

def validate_ticker(ticker: str) -> bool:
    """Validasi format ticker saham (contoh: BBCA.JK)"""
    return isinstance(ticker, str) and len(ticker.split('.')) == 2

def validate_date_range(start_date: datetime, end_date: datetime) -> bool:
    """Validasi range tanggal"""
    return start_date < end_date if start_date and end_date else False

def validate_investment_amount(amount: float) -> bool:
    """Validasi jumlah investasi"""
    return amount >= 100000  # Minimal Rp100,000
