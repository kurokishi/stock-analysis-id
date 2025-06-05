import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from utils.data_fetcher import DataFetcher
from utils.validator import StockValidator

def compare_stocks(tickers):
    st.subheader("🆚 Perbandingan Saham")
    
    # Validasi input
    if not tickers or len(tickers) < 2:
        st.warning("""
        Masukkan minimal 2 kode saham yang valid untuk dibandingkan.
        Contoh format: ['BBCA.JK', 'TLKM.JK'] atau ['AAPL', 'MSFT']
        """)
        return
    
    try:
        valid_tickers = StockValidator.filter_valid_tickers(tickers)
        st.write("Ticker yang divalidasi:", valid_tickers)  # Debug
        
        if len(valid_tickers) < 2:
            st.warning(f"""
            Hanya ditemukan {len(valid_tickers)} ticker valid.
            Ticker yang dimasukkan: {tickers}
            Ticker valid: {valid_tickers}
            """)
            return
            
        # Ambil data untuk semua ticker
        data = {}
        for ticker in valid_tickers:
            df = DataFetcher.get_stock_data(ticker)
            if not df.empty:
                data[ticker] = df['Close']
            else:
                st.warning(f"Data untuk {ticker} tidak tersedia")
    
    # Normalisasi harga untuk perbandingan
    comparison_df = pd.DataFrame(data).dropna()
    if len(comparison_df) == 0:
        st.error("Tidak ada periode yang sama untuk dibandingkan")
        return
    
    comparison_df = comparison_df / comparison_df.iloc[0] * 100
    
    # Plot perbandingan
    st.subheader("📈 Perbandingan Kinerja")
    fig = go.Figure()
    
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']  # Warna berbeda
    
    for i, ticker in enumerate(comparison_df.columns):
        fig.add_trace(go.Scatter(
            x=comparison_df.index,
            y=comparison_df[ticker],
            name=ticker,
            mode='lines',
            line=dict(color=colors[i % len(colors)], width=2),
            hovertemplate=f"{ticker}: %{{y:.2f}}%"
        ))
    
    fig.update_layout(
        title="Perbandingan Kinerja Saham (Normalisasi 100 pada awal periode)",
        xaxis_title="Tanggal",
        yaxis_title="Kinerja (%)",
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Analisis performa relatif
    st.subheader("📊 Analisis Performa")
    start_date = comparison_df.index[0].strftime('%d %b %Y')
    end_date = comparison_df.index[-1].strftime('%d %b %Y')
    
    # Hitung metrik performa
    performance_data = []
    for ticker in comparison_df.columns:
        returns = (comparison_df[ticker].iloc[-1] - 100) / 100
        volatility = comparison_df[ticker].pct_change().std() * np.sqrt(252)  # Annualized
        sharpe_ratio = returns / volatility if volatility > 0 else 0
        max_drawdown = (comparison_df[ticker] / comparison_df[ticker].cummax() - 1).min() * 100
        
        performance_data.append({
            'Saham': ticker,
            'Return (%)': f"{returns * 100:.2f}%",
            'Volatilitas Tahunan (%)': f"{volatility * 100:.2f}%",
            'Sharpe Ratio': f"{sharpe_ratio:.2f}",
            'Max Drawdown (%)': f"{max_drawdown:.2f}%"
        })
    
    # Tampilkan tabel performa
    st.dataframe(
        pd.DataFrame(performance_data).sort_values('Return (%)', ascending=False),
        use_container_width=True
    )
    
    # Korelasi antar saham
    st.subheader("📌 Korelasi Antar Saham")
    returns_df = comparison_df.pct_change().dropna()
    correlation_matrix = returns_df.corr()
    
    fig2 = go.Figure(data=go.Heatmap(
        z=correlation_matrix,
        x=correlation_matrix.columns,
        y=correlation_matrix.columns,
        colorscale='RdBu',
        zmin=-1,
        zmax=1,
        hoverongaps=False,
        text=correlation_matrix.round(2),
        texttemplate="%{text}"
    ))
    fig2.update_layout(
        title="Korelasi Return Harian",
        xaxis_title="Saham",
        yaxis_title="Saham"
    )
    st.plotly_chart(fig2, use_container_width=True)
    
    st.caption(f"Periode analisis: {start_date} hingga {end_date}")
    
except Exception as e:
        st.error(f"Terjadi error saat memproses perbandingan: {str(e)}")
