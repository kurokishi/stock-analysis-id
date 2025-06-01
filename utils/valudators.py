from datetime import datetime

def validate_ticker(ticker: str) -> bool:
    return isinstance(ticker, str) and len(ticker.split('.')) == 2

def validate_date_range(start_date, end_date) -> bool:
    return start_date < end_date if start_date and end_date else False
