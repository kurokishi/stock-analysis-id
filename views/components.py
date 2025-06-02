import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from utils.formatters import format_rupiah, format_percent

class StockComponents:
    @staticmethod
    def display_stock_chart(data: pd.DataFrame, ticker: str, indicators: list = None):
        """
        Menampilkan grafik harga saham menggunakan Plotly.
        
        Parameters:
        -----------
        data : pd.DataFrame
            DataFrame dengan kolom 'dates' dan 'closes'
        ticker : str
            Kode saham/ticker
        indicators : list, optional
            List indikator tambahan untuk ditampilkan di grafik
        """
        if data.empty:
            st.warning("Data kosong, tidak dapat menampilkan grafik")
            return
            
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=data['dates'],
            y=data['closes'],
            name='Harga Penutupan',
            line=dict(color='blue')
        ))
        
        if indicators:
            for indicator in indicators:
                if isinstance(indicator, dict) and 'x' in indicator and 'y' in indicator:
                    fig.add_trace(go.Scatter(**indicator))
        
        fig.update_layout(
            title=f"Harga Saham {ticker}",
            xaxis_title="Tanggal",
            yaxis_title="Harga (Rp)",
            hovermode="x unified"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    @staticmethod
    def display_quick_stats(data: pd.DataFrame):
        """
        Menampilkan statistik cepat saham.
        
        Parameters:
        -----------
        data : pd.DataFrame
            DataFrame dengan kolom 'closes' dan 'volumes'
        """
        if data.empty or len(data) < 2:
            st.warning("Data tidak cukup untuk menampilkan statistik")
            return
            
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Harga Terakhir", format_rupiah(data['closes'].iloc[-1]))
        with col2:
            change = data['closes'].iloc[-1] - data['closes'].iloc[-2]
            pct_change = (change / data['closes'].iloc[-2]) * 100
            st.metric("Perubahan Hari Ini", 
                     format_rupiah(change), 
                     f"{pct_change:.2f}%")
        with col3:
            st.metric("Volume Hari Ini", f"{data['volumes'].iloc[-1]:,}".replace(",", "."))

    @staticmethod
    def display_technical_charts(stock_data: dict, ticker: str):
        """
        Menampilkan grafik analisis teknikal.
        
        Parameters:
        -----------
        stock_data : dict
            Dictionary dengan struktur:
            {
                'dates': list,
                'closes': list,
                'indicators': {
                    'sma_20': list,
                    'sma_50': list,
                    'rsi': list,
                    'macd': list
                }
            }
        ticker : str
            Kode saham/ticker
        """
        if not stock_data or not stock_data.get('dates'):
            st.warning("Data teknikal tidak tersedia")
            return
            
        try:
            df = pd.DataFrame({
                'date': stock_data['dates'],
                'close': stock_data['closes'],
                'SMA_20': stock_data['indicators'].get('sma_20', []),
                'SMA_50': stock_data['indicators'].get('sma_50', []),
                'RSI': stock_data['indicators'].get('rsi', []),
                'MACD': stock_data['indicators'].get('macd', [])
            })
            
            # Grafik harga dan moving average
            fig1 = go.Figure()
            fig1.add_trace(go.Scatter(x=df['date'], y=df['close'], name='Harga'))
            
            if 'SMA_20' in df and not df['SMA_20'].empty:
                fig1.add_trace(go.Scatter(x=df['date'], y=df['SMA_20'], name='SMA 20'))
            if 'SMA_50' in df and not df['SMA_50'].empty:
                fig1.add_trace(go.Scatter(x=df['date'], y=df['SMA_50'], name='SMA 50'))
                
            fig1.update_layout(
                title=f"Moving Averages - {ticker}",
                hovermode="x unified"
            )
            st.plotly_chart(fig1, use_container_width=True)
            
            # Grafik RSI jika ada
            if 'RSI' in df and not df['RSI'].empty:
                fig2 = go.Figure()
                fig2.add_trace(go.Scatter(x=df['date'], y=df['RSI'], name='RSI'))
                fig2.add_hline(y=30, line_dash="dash", line_color="green")
                fig2.add_hline(y=70, line_dash="dash", line_color="red")
                fig2.update_layout(
                    title=f"RSI (14) - {ticker}",
                    hovermode="x unified"
                )
                st.plotly_chart(fig2, use_container_width=True)
                
        except Exception as e:
            st.error(f"Gagal menampilkan grafik teknikal: {str(e)}")
