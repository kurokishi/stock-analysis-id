from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, List

@dataclass
class StockData:
    """
    Model data time series saham
    """
    ticker: str
    dates: List[datetime]
    opens: List[float]
    highs: List[float]
    lows: List[float]
    closes: List[float]
    volumes: List[int]
    
    def to_dataframe(self):
        """Convert to pandas DataFrame"""
        import pandas as pd
        return pd.DataFrame({
            'Open': self.opens,
            'High': self.highs,
            'Low': self.lows,
            'Close': self.closes,
            'Volume': self.volumes
        }, index=self.dates)

@dataclass
class StockInfo:
    """
    Model informasi fundamental saham
    """
    ticker: str
    name: str
    sector: str
    industry: str
    country: str
    currency: str
    market_cap: float
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    dividend_yield: Optional[float] = None
    roe: Optional[float] = None  # Return on Equity
    roa: Optional[float] = None  # Return on Assets
    debt_to_equity: Optional[float] = None
    
    def get_summary(self) -> Dict[str, str]:
        """Return summary as dictionary"""
        return {
            'Ticker': self.ticker,
            'Nama Perusahaan': self.name,
            'Sektor': self.sector,
            'Industri': self.industry,
            'Negara': self.country,
            'Kapitalisasi Pasar': f"Rp{self.market_cap:,.2f}",
            'P/E Ratio': str(self.pe_ratio) if self.pe_ratio else 'N/A',
            'P/B Ratio': str(self.pb_ratio) if self.pb_ratio else 'N/A',
            'Dividen Yield': f"{self.dividend_yield:.2%}" if self.dividend_yield else 'N/A'
        }
