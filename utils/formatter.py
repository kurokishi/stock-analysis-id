# utils/formatter.py
def format_rupiah(value):
    """Format nilai ke Rupiah"""
    try:
        return f"Rp{round(value):,}".replace(",", ".")
    except (TypeError, ValueError):
        return "Rp0"

# Tambahkan fungsi lain jika diperlukan
def format_percent(value):
    """Format nilai ke persentase"""
    try:
        return f"{value:.2f}%"
    except (TypeError, ValueError):
        return "0%"
