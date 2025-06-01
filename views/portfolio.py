import streamlit as st
from datetime import datetime
from core.portfolio import PortfolioAnalyzer
from views.components import StockComponents

class PortfolioView:
    def __init__(self, data_provider):
        self.analyzer = PortfolioAnalyzer(data_provider)
        self.components = StockComponents()
    
    def show_portfolio_simulation(self, ticker):
        st.subheader("💰 Simulasi Portofolio Saham")
        
        col1, col2 = st.columns(2)
        with col1:
            initial_investment = st.number_input(
                "Jumlah Investasi Awal (Rp)",
                min_value=100000,
                value=10000000,
                step=100000
            )
        with col2:
            investment_date = st.date_input(
                "Tanggal Investasi",
                value=datetime.now() - timedelta(days=180),
                min_value=datetime(2010,1,1),
                max_value=datetime.today()
            )
        
        if st.button("Hitung Simulasi"):
            try:
                result = self.analyzer.simulate_portfolio(
                    ticker,
                    initial_investment,
                    investment_date
                )
                
                # Tampilkan metrik utama
                cols = st.columns(3)
                cols[0].metric("Nilai Awal", format_rupiah(initial_investment))
                cols[1].metric(
                    "Nilai Sekarang", 
                    format_rupiah(result['current_value']),
                    f"{result['profit_pct']:.2f}%"
                )
                cols[2].metric(
                    "Keuntungan/Rugi", 
                    format_rupiah(result['profit'])
                )
                
                # Tampilkan grafik
                self._display_portfolio_chart(result['history'])
                
                # Hitung dan tampilkan metrik risiko
                risk_metrics = self.analyzer.calculate_risk_metrics(result['history'])
                if risk_metrics:
                    st.subheader("📉 Analisis Risiko")
                    risk_cols = st.columns(3)
                    risk_cols[0].metric(
                        "Volatilitas Tahunan", 
                        f"{risk_metrics['annual_volatility']:.2%}"
                    )
                    risk_cols[1].metric(
                        "Max Drawdown", 
                        f"{risk_metrics['max_drawdown_pct']:.2f}%"
                    )
                    risk_cols[2].metric(
                        "Sharpe Ratio", 
                        f"{risk_metrics['sharpe_ratio']:.2f}"
                    )
                
                # Generate report
                st.subheader("📋 Laporan Lengkap")
                st.text(self.analyzer.generate_report(result, risk_metrics))
                
            except ValueError as e:
                st.error(str(e))
    
    def _display_portfolio_chart(self, history):
        fig = history['portfolio_value'].plot(
            kind='line',
            title='Kinerja Portofolio',
            xlabel='Tanggal',
            ylabel='Nilai (Rp)',
            figsize=(10, 5)
        ).get_figure()
        st.pyplot(fig)
