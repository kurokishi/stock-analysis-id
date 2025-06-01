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
