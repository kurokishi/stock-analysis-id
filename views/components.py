import streamlit as st
import plotly.graph_objects as go
from utils.formatters import format_rupiah, format_percent

class StockComponents:
    @staticmethod
    def display_stock_chart(data, ticker, indicators=None):
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=data['dates'],
            y=data['closes'],
            name='Harga Penutupan',
            line=dict(color='blue')
        ))
        
        if indicators:
            for indicator in indicators:
                fig.add_trace(indicator)
        
        fig.update_layout(
            title=f"Harga Saham {ticker}",
            xaxis_title="Tanggal",
            yaxis_title="Harga (Rp)"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    @staticmethod
    def display_quick_stats(data):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Harga Terakhir", format_rupiah(data['closes'][-1]))
        with col2:
            change = data['closes'][-1] - data['closes'][-2]
            pct_change = (change / data['closes'][-2]) * 100
            st.metric("Perubahan Hari Ini", 
                     format_rupiah(change), 
                     f"{pct_change:.2f}%")
        with col3:
            st.metric("Volume Hari Ini", f"{data['volumes'][-1]:,}".replace(",", "."))

def display_technical_charts(self, stock_data, ticker):
    """Tampilkan grafik teknikal"""
    df = pd.DataFrame({
        'date': stock_data.dates,
        'close': stock_data.closes,
        'SMA_20': stock_data.indicators.get('sma_20', []),
        'SMA_50': stock_data.indicators.get('sma_50', []),
        'RSI': stock_data.indicators.get('rsi', []),
        'MACD': stock_data.indicators.get('macd', [])
    })
    
    # Grafik harga dan moving average
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=df['date'], y=df['close'], name='Harga'))
    if 'SMA_20' in df:
        fig1.add_trace(go.Scatter(x=df['date'], y=df['SMA_20'], name='SMA 20'))
    if 'SMA_50' in df:
        fig1.add_trace(go.Scatter(x=df['date'], y=df['SMA_50'], name='SMA 50'))
    fig1.update_layout(title=f"Moving Averages - {ticker}")
    st.plotly_chart(fig1, use_container_width=True)
    
    # Grafik RSI jika ada
    if 'RSI' in df:
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=df['date'], y=df['RSI'], name='RSI'))
        fig2.add_hline(y=30, line_dash="dash", line_color="green")
        fig2.add_hline(y=70, line_dash="dash", line_color="red")
        fig2.update_layout(title=f"RSI (14) - {ticker}")
        st.plotly_chart(fig2, use_container_width=True)
