from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import pandas as pd
import numpy as np
from models.stock import StockData
from utils.formatters import format_rupiah

class PortfolioAnalyzer:
    def __init__(self, data_provider):
        self.data_provider = data_provider
    
    def simulate_portfolio(
        self,
        ticker: str,
        initial_investment: float,
        investment_date: datetime
    ) -> Dict:
        """
        Simulasi kinerja portofolio saham
        
        Args:
            ticker: Kode saham (contoh: 'BBCA.JK')
            initial_investment: Jumlah investasi awal dalam Rupiah
            investment_date: Tanggal pembelian saham
            
        Returns:
            Dict berisi:
            - shares: Jumlah lembar saham
            - current_value: Nilai portofolio saat ini
            - profit: Keuntungan/kerugian
            - profit_pct: Persentase keuntungan
            - history: Data historis performa portofolio
        """
        stock_data = self.data_provider.get_stock_data(ticker)
        
        if not stock_data.dates:
            raise ValueError("Data saham tidak tersedia")
        
        # Konversi ke DataFrame
        df = pd.DataFrame({
            'date': stock_data.dates,
            'close': stock_data.closes
        }).set_index('date')
        
        # Cari tanggal terdekat setelah tanggal investasi
        mask = df.index >= pd.to_datetime(investment_date)
        if not any(mask):
            raise ValueError("Tidak ada data untuk tanggal tersebut")
        
        start_price = df[mask].iloc[0]['close']
        current_price = df.iloc[-1]['close']
        
        # Hitung kinerja
        shares = initial_investment / start_price
        current_value = shares * current_price
        profit = current_value - initial_investment
        profit_pct = (profit / initial_investment) * 100
        
        # Siapkan data historis
        df['portfolio_value'] = (df['close'] / start_price) * initial_investment
        
        return {
            'shares': shares,
            'current_value': current_value,
            'profit': profit,
            'profit_pct': profit_pct,
            'history': df[['close', 'portfolio_value']]
        }
    
    def compare_portfolios(
        self,
        investments: List[Tuple[str, float, datetime]]
    ) -> Dict[str, Dict]:
        """
        Bandingkan beberapa portofolio saham sekaligus
        
        Args:
            investments: List berisi tuple (ticker, jumlah_investasi, tanggal)
            
        Returns:
            Dict berisi hasil simulasi untuk masing-masing ticker
        """
        results = {}
        
        for ticker, amount, date in investments:
            try:
                result = self.simulate_portfolio(ticker, amount, date)
                results[ticker] = result
            except ValueError as e:
                results[ticker] = {'error': str(e)}
                
        return results
    
    def calculate_risk_metrics(
        self,
        portfolio_history: pd.DataFrame
    ) -> Dict[str, float]:
        """
        Hitung metrik risiko portofolio
        
        Args:
            portfolio_history: DataFrame dengan kolom 'portfolio_value'
            
        Returns:
            Dict berisi berbagai metrik risiko
        """
        returns = portfolio_history['portfolio_value'].pct_change().dropna()
        
        if len(returns) < 2:
            return {}
        
        volatility = returns.std() * np.sqrt(252)  # Annualized
        max_drawdown = (returns.min() - 1) * 100  # Dalam persen
        sharpe_ratio = returns.mean() / returns.std() * np.sqrt(252)
        
        return {
            'annual_volatility': volatility,
            'max_drawdown_pct': max_drawdown,
            'sharpe_ratio': sharpe_ratio
        }
    
    def generate_report(
        self,
        simulation_result: Dict,
        risk_metrics: Dict
    ) -> str:
        """
        Hasilkan laporan teks dari hasil simulasi
        
        Args:
            simulation_result: Hasil dari simulate_portfolio()
            risk_metrics: Hasil dari calculate_risk_metrics()
            
        Returns:
            String laporan yang sudah diformat
        """
        report = [
            "📊 Laporan Portofolio Saham",
            "==========================",
            f"Jumlah Saham: {simulation_result['shares']:.2f} lembar",
            f"Nilai Awal: {format_rupiah(simulation_result['history'].iloc[0]['portfolio_value'])}",
            f"Nilai Sekarang: {format_rupiah(simulation_result['current_value'])}",
            f"Keuntungan: {format_rupiah(simulation_result['profit'])} "
            f"({simulation_result['profit_pct']:.2f}%)",
            "",
            "📈 Metrik Risiko",
            "---------------"
        ]
        
        if risk_metrics:
            report.extend([
                f"Volatilitas Tahunan: {risk_metrics['annual_volatility']:.2%}",
                f"Max Drawdown: {risk_metrics['max_drawdown_pct']:.2f}%",
                f"Sharpe Ratio: {risk_metrics['sharpe_ratio']:.2f}"
            ])
        else:
            report.append("Data tidak cukup untuk menghitung metrik risiko")
            
        return "\n".join(report)
