# views/dashboard_view.py
import streamlit as st
from plotly.graph_objects import Figure, Scatter
from utils.data_fetcher import DataFetcher
from utils.formatter import format_rupiah
from views.fundamental_view import show_fundamental_analysis
from views.news_sentiment import get_news_sentiment

def show_dashboard(ticker):
    """Menampilkan dashboard utama untuk satu saham"""
    # Validasi input
    if not ticker or not isinstance(ticker, str):
        st.error("Format ticker tidak valid")
        return
    
    st.subheader(f"📈 Dashboard Saham {ticker}")
    data = DataFetcher.get_stock_data(ticker)
    
    if data is None or data.empty:
        st.error("Gagal memuat data saham")
        return
        
    if len(data) < 2:
        st.warning("Data historis tidak cukup")
        return

    # Visualisasi Plotly
    fig = Figure()
    fig.add_trace(Scatter(
        x=data.index, 
        y=data['Close'], 
        name='Harga Penutupan',
        line=dict(color='#1f77b4')
    )
    fig.update_layout(
        title=f"Performa Saham {ticker}",
        xaxis_title="Tanggal",
        yaxis_title="Harga (Rp)",
        hovermode="x unified"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Statistik utama
    col1, col2, col3 = st.columns(3)
    last_close = data['Close'].iloc[-1]
    
    with col1:
        st.metric("Harga Terakhir", format_rupiah(last_close))
        
    with col2:
        change = last_close - data['Close'].iloc[-2]
        pct_change = (change / data['Close'].iloc[-2]) * 100
        st.metric(
            "Perubahan Hari Ini", 
            f"{format_rupiah(change)} ({pct_change:.2f}%)",
            delta_color="inverse"
        )
        
    with col3:
        vol = int(data['Volume'].iloc[-1]/1000)
        st.metric("Volume", f"{vol:,}K".replace(",", "."))
    
    # Komponen tambahan
    show_fundamental_analysis(ticker)
    get_news_sentiment(ticker)
