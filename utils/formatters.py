from datetime import datetime
from typing import Union

def format_rupiah(value: Union[int, float]) -> str:
    try:
        return f"Rp{round(value):,}".replace(",", ".")
    except (TypeError, ValueError):
        return "Rp0"

def format_percent(value: float) -> str:
    try:
        return f"{value:.2%}"
    except (TypeError, ValueError):
        return "0%"

def format_date(date: datetime, fmt: str = "%d %b %Y") -> str:
    try:
        return date.strftime(fmt)
    except (TypeError, ValueError):
        return "-"
