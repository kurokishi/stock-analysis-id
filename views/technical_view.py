import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from utils.data_fetcher import DataFetcher

def add_technical_indicators(data):
    """Menambahkan indikator teknikal ke data saham"""
    if data.empty:
        return data
    
    # Simple Moving Averages
    data['SMA_20'] = data['Close'].rolling(window=20).mean()
    data['SMA_50'] = data['Close'].rolling(window=50).mean()
    
    # RSI
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    data['RSI'] = 100 - (100 / (1 + rs))
    
    # MACD
    exp12 = data['Close'].ewm(span=12, adjust=False).mean()
    exp26 = data['Close'].ewm(span=26, adjust=False).mean()
    data['MACD'] = exp12 - exp26
    data['Signal'] = data['MACD'].ewm(span=9, adjust=False).mean()
    
    return data

def plot_technical_indicators(data, ticker):
    """Plot indikator teknikal"""
    if data.empty:
        st.warning("Data tidak tersedia untuk analisis teknikal")
        return
    
    # Price with Moving Averages
    st.subheader("📈 Moving Averages")
    fig1 = go.Figure()
    fig1.add_trace(go.Candlestick(
        x=data.index,
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'],
        name='Harga'
    ))
    fig1.add_trace(go.Scatter(
        x=data.index, 
        y=data['SMA_20'], 
        name='SMA 20',
        line=dict(color='orange', width=2)
    ))
    fig1.add_trace(go.Scatter(
        x=data.index, 
        y=data['SMA_50'], 
        name='SMA 50',
        line=dict(color='blue', width=2)
    ))
    fig1.update_layout(
        title=f"{ticker} - Harga dan Moving Averages",
        xaxis_rangeslider_visible=False
    )
    st.plotly_chart(fig1, use_container_width=True)
    
    # RSI
    st.subheader("📊 RSI (Relative Strength Index)")
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=data.index, 
        y=data['RSI'], 
        name='RSI',
        line=dict(color='purple', width=2)
    ))
    fig2.add_hline(y=30, line_dash="dash", line_color="green")
    fig2.add_hline(y=70, line_dash="dash", line_color="red")
    fig2.update_layout(
        yaxis_range=[0,100],
        title="RSI (14 hari) - Level 30-70 menunjukkan overbought/oversold"
    )
    st.plotly_chart(fig2, use_container_width=True)
    
    # MACD
    st.subheader("📉 MACD (Moving Average Convergence Divergence)")
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(
        x=data.index, 
        y=data['MACD'], 
        name='MACD',
        line=dict(color='blue', width=2)
    ))
    fig3.add_trace(go.Scatter(
        x=data.index, 
        y=data['Signal'], 
        name='Signal Line',
        line=dict(color='orange', width=2)
    ))
    # Tambahkan area untuk sinyal beli/jual
    fig3.add_trace(go.Scatter(
        x=data.index,
        y=[0]*len(data),
        fill='tonexty',
        fillcolor='rgba(0,100,80,0.2)',
        line=dict(color='rgba(255,255,255,0)'),
        showlegend=False
    ))
    fig3.update_layout(title="MACD - Sinyal beli ketika MACD melewati Signal Line dari bawah")
    st.plotly_chart(fig3, use_container_width=True)

def show_technical_analysis(ticker):
    """Menampilkan analisis teknikal lengkap"""
    st.subheader("🔧 Analisis Teknikal")
    
    # Ambil data
    data = DataFetcher.get_stock_data(ticker)
    if data.empty:
        st.warning("Data saham tidak tersedia")
        return
    
    # Tambahkan indikator
    data_with_indicators = add_technical_indicators(data)
    
    # Tampilkan indikator
    plot_technical_indicators(data_with_indicators, ticker)
    
    # Tabel data
    st.subheader("📋 Data Teknikal")
    st.dataframe(
        data_with_indicators[['Close', 'SMA_20', 'SMA_50', 'RSI', 'MACD', 'Signal']].tail(20).style.format({
            'Close': '{:.2f}',
            'SMA_20': '{:.2f}',
            'SMA_50': '{:.2f}',
            'RSI': '{:.2f}',
            'MACD': '{:.4f}',
            'Signal': '{:.4f}'
        }),
        use_container_width=True
    )
