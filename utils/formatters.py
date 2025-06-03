def format_rupiah(value):
    """Format nilai ke Rupiah"""
    try:
        return f"Rp{round(value):,}".replace(",", ".")
    except (TypeError, ValueError):
        return "Rp0"
