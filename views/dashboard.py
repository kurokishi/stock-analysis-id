import streamlit as st
from views.components import StockComponents
from models.stock import StockData

class DashboardView:
    def __init__(self, data_provider):
        self.data_provider = data_provider
        self.components = StockComponents()

    def show(self, ticker):
        st.subheader("📈 Dashboard Saham")
        stock_data = self.data_provider.get_stock_data(ticker)
        
        if not stock_data.dates:
            st.warning("Data saham tidak tersedia")
            return
            
        self.components.display_stock_chart(
            stock_data.__dict__,
            ticker
        )
        self.components.display_quick_stats(stock_data.__dict__)
        
        st.subheader("📊 Info Fundamental")
        stock_info = self.data_provider.get_stock_info(ticker)
        st.json(stock_info.get_summary())

    def show_portfolio_simulation(self, ticker):
        # Implementasi simulasi portofolio
        pass

    def compare_stocks(self, tickers):
        # Implementasi perbandingan saham
        pass
