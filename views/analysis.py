import streamlit as st
from core.data_provider import StockDataProvider
from core.analysis import FundamentalAnalyzer, TechnicalAnalyzer
from views.components import StockComponents

class AnalysisView:
    def __init__(self, data_provider):
        self.data_provider = data_provider
        self.components = StockComponents()
    
    def show_fundamental(self, ticker):
        st.subheader("📊 Analisis Fundamental")
        stock_info = self.data_provider.get_stock_info(ticker)
        
        if stock_info.name == 'N/A':
            st.warning("Data fundamental tidak tersedia")
            return
            
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**Info Perusahaan**")
            st.write(f"Nama: {stock_info.name}")
            st.write(f"Sektor: {stock_info.sector}")
            st.write(f"Industri: {stock_info.industry}")
            st.write(f"Negara: {stock_info.country}")
        
        with col2:
            st.markdown("**Valuasi**")
            st.write(f"P/E: {stock_info.pe_ratio or 'N/A'}")
            st.write(f"P/B: {stock_info.pb_ratio or 'N/A'}")
            st.write(f"Dividen Yield: {stock_info.dividend_yield or 'N/A'}")
        
        with col3:
            st.markdown("**Kinerja**")
            st.write(f"Kapitalisasi Pasar: Rp{stock_info.market_cap:,.2f}")
            st.write(f"ROE: {stock_info.roe or 'N/A'}")
            st.write(f"ROA: {stock_info.roa or 'N/A'}")

    def show_technical(self, ticker):
        st.subheader("📈 Analisis Teknikal")
        stock_data = self.data_provider.get_stock_data(ticker)
        
        if not stock_data.dates:
            st.warning("Data saham tidak tersedia")
            return
            
        # Tambahkan indikator teknikal
        analyzer = TechnicalAnalyzer()
        analyzed_data = analyzer.add_technical_indicators(stock_data)
        
        # Tampilkan grafik
        self.components.display_technical_charts(analyzed_data, ticker)
