import streamlit as st
from views.components import StockComponents
from models.stock import StockData

class DashboardView:
    def __init__(self, data_provider):
        self.data_provider = data_provider
        self.components = StockComponents()

    # Di views/dashboard.py
def show(self, ticker):
    stock_data = self.data_provider.get_stock_data(ticker)
    if not stock_data:
        st.warning("Data saham tidak tersedia")
        return
    
    # Konversi ke DataFrame sebelum dikirim ke components
    df = pd.DataFrame({
        'dates': stock_data.dates,
        'closes': stock_data.closes,
        'volumes': stock_data.volumes
    })
    
    self.components.display_stock_chart(df, ticker)

    def show_portfolio_simulation(self, ticker):
        # Implementasi simulasi portofolio
        pass

    def compare_stocks(self, tickers):
        # Implementasi perbandingan saham
        pass
