import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils.data_fetcher import DataFetcher
from utils.formatter import format_rupiah
from utils.validator import StockValidator

def portfolio_simulation(ticker):
    """Menampilkan simulasi portofolio investasi"""
    st.subheader("💰 Simulasi Portofolio")
    
    # Ambil data saham
    data = DataFetcher.get_stock_data(ticker)
    if data.empty:
        st.warning("Data tidak tersedia untuk simulasi")
        return
    
    # Input parameter simulasi
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
            min_value=data.index[0].date(),
            max_value=data.index[-1].date()
        )
    
    if st.button("Hitung Kinerja", key="portfolio_calculate"):
        # Validasi input
        try:
            initial_investment = float(initial_investment)
            if not StockValidator.validate_investment_amount(initial_investment):
                st.error("Jumlah investasi minimal Rp100.000")
                return
        except ValueError:
            st.error("Masukkan jumlah investasi yang valid")
            return
            
        # Konversi ke datetime tanpa timezone
        investment_date = pd.to_datetime(investment_date).tz_localize(None)
        
        if investment_date < data.index[0] or investment_date > data.index[-1]:
            st.error("Tanggal investasi tidak valid")
            return
        
        # Temukan hari bursa terdekat
        mask = data.index >= investment_date
        if not any(mask):
            st.error("Tidak ada data untuk tanggal tersebut")
            return
        
        start_price = data.loc[mask].iloc[0]['Close']
        current_price = data['Close'].iloc[-1]
        
        # Hitung kinerja
        shares = initial_investment / start_price
        current_value = shares * current_price
        profit = current_value - initial_investment
        profit_pct = (profit / initial_investment) * 100
        
        # Tampilkan hasil
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Nilai Awal", format_rupiah(initial_investment))
        with col2:
            st.metric(
                "Nilai Sekarang", 
                format_rupiah(current_value), 
                f"{profit_pct:.2f}%"
            )
        with col3:
            st.metric("Keuntungan/Rugi", format_rupiah(profit))
        
        # Grafik kinerja
        st.subheader("📈 Kinerja Portofolio")
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['Close'] / start_price * initial_investment,
            name='Nilai Portofolio',
            line=dict(color='green')
        ))
       
        if isinstance(investment_date, pd.Timestamp):
            investment_date = investment_date.to_pydatetime()

        fig.add_vline(
            x=investment_date,
            line_dash="dash",
            line_color="red",
            annotation_text="Investasi Awal",
            annotation_position="top"
        )
        
        fig.update_layout(
            title="Perkembangan Nilai Portofolio",
            xaxis_title="Tanggal",
            yaxis_title="Nilai (Rp)",
            hovermode="x unified"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Analisis tambahan
        st.subheader("📊 Analisis Tambahan")
        
        # Hitung drawdown
        portfolio_values = data['Close'] / start_price * initial_investment
        peak = portfolio_values.expanding(min_periods=1).max()
        drawdown = (portfolio_values - peak) / peak * 100
        
        # Volatilitas
        daily_returns = data['Close'].pct_change().dropna()
        annualized_volatility = daily_returns.std() * np.sqrt(252) * 100
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Drawdown Maksimum", f"{drawdown.min():.2f}%")
        with col2:
            st.metric("Volatilitas Tahunan", f"{annualized_volatility:.2f}%")
        
        # Grafik drawdown
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=data.index,
            y=drawdown,
            name='Drawdown',
            fill='tozeroy',
            fillcolor='rgba(255,0,0,0.2)',
            line=dict(color='red')
        ))
        fig2.update_layout(
            title="Drawdown Portofolio",
            xaxis_title="Tanggal",
            yaxis_title="Drawdown (%)",
            yaxis_tickformat=".2f%"
        )
        st.plotly_chart(fig2, use_container_width=True)
