# views/dashboard_view.py
import streamlit as st
import plotly.graph_objects as go
from utils.data_fetcher import DataFetcher
from utils.formatter import format_rupiah
from utils.validator import StockValidator
from views.fundamental_view import show_fundamental_analysis
from views.news_sentiment import get_news_sentiment

def show_dashboard(ticker):
    """Menampilkan dashboard utama untuk satu saham"""
    # Pindahkan validasi ke dalam fungsi
    if not StockValidator.validate_ticker(ticker):
        st.error("Format ticker tidak valid")
        return
    
    st.subheader("📈 Grafik Harga Saham")
    data = DataFetcher.get_stock_data(ticker)
    
    if not data.empty:
        # Plot harga saham
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=data.index, 
            y=data['Close'], 
            name='Harga Penutupan'
        ))
        fig.update_layout(
            title=f"Harga Saham {ticker}",
            xaxis_title="Tanggal",
            yaxis_title="Harga (Rp)"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Statistik cepat
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Harga Terakhir", format_rupiah(data['Close'].iloc[-1]))
        with col2:
            change = data['Close'].iloc[-1] - data['Close'].iloc[-2]
            pct_change = (change / data['Close'].iloc[-2]) * 100
            st.metric("Perubahan Hari Ini", format_rupiah(change), f"{pct_change:.2f}%")
        with col3:
            st.metric("Volume Hari Ini", f"{data['Volume'].iloc[-1]:,}".replace(",", "."))
        
        # Analisis fundamental dan sentimen berita
        show_fundamental_analysis(ticker)
        get_news_sentiment(ticker)
    else:
        st.warning("Data saham tidak tersedia")
