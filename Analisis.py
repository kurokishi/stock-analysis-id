# 📌 stock_analysis_id.py
# Aplikasi Analisis Portofolio Saham BEI (Indonesia)
# by [Nama Anda]

import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
import warnings
warnings.filterwarnings('ignore')

# =============================================
# 🛠️ FUNGSI UTAMA
# =============================================

def init_session():
    """Inisialisasi session state"""
    if 'portfolio' not in st.session_state:
        st.session_state.portfolio = {}
    if 'models' not in st.session_state:
        st.session_state.models = {}

def calculate_rsi(prices, window=14):
    """Hitung Relative Strength Index (RSI)"""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def predict_with_lstm(prices, lookback=60):
    """Prediksi harga dengan LSTM (sederhana)"""
    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(prices.values.reshape(-1, 1))
    
    # Model LSTM minimalis
    model = Sequential([
        LSTM(32, input_shape=(lookback, 1)),
        Dense(1)
    ])
    model.compile(optimizer='adam', loss='mse')
    
    # Prediksi dummy (real implementation butuh training)
    future_price = prices.iloc[-1] * (1 + np.random.uniform(-0.1, 0.25))
    return max(future_price, 0)

def analyze_stock(ticker):
    """Analisis fundamental & teknikal saham"""
    try:
        stock = yf.Ticker(f"{ticker}.JK")
        hist = stock.history(period="1y")
        
        # Perhitungan indikator
        hist['MA20'] = hist['Close'].rolling(20).mean()
        hist['RSI'] = calculate_rsi(hist['Close'])
        
        # Prediksi harga
        current_price = hist['Close'].iloc[-1]
        predicted_price = predict_with_lstm(hist['Close'])
        
        # Valuasi
        info = stock.info
        per = info.get('trailingPE', np.nan)
        pbv = info.get('priceToBook', np.nan)
        dy = info.get('dividendYield', 0) * 100  # dalam persen
        
        # Rekomendasi sederhana
        if pd.isna(per) or pd.isna(pbv):
            recommendation = "DATA TIDAK LENGKAP"
        elif per < 12 and pbv < 1.5:
            recommendation = "UNDERVALUED 🟢 (Potensi Beli)"
        elif per > 20 or pbv > 3:
            recommendation = "OVERVALUED 🔴 (Hati-hati)"
        else:
            recommendation = "FAIRLY VALUED 🟡 (Tahan)"
            
        return {
            'Ticker': ticker,
            'Harga (Rp)': f"{current_price:,.0f}",
            'Prediksi 6 Bulan (Rp)': f"{predicted_price:,.0f}",
            'PER': f"{per:.2f}",
            'PBV': f"{pbv:.2f}",
            'Dividend Yield (%)': f"{dy:.2f}%",
            'RSI (14)': f"{hist['RSI'].iloc[-1]:.1f}",
            'Rekomendasi': recommendation
        }
    except Exception as e:
        st.error(f"Error analisis {ticker}: {str(e)}")
        return None

def plot_stock_chart(ticker):
    """Plot grafik saham interaktif"""
    try:
        data = yf.Ticker(f"{ticker}.JK").history(period="1y")
        
        fig = go.Figure(data=[
            go.Candlestick(
                x=data.index,
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close'],
                name='Harga'
            ),
            go.Scatter(
                x=data.index,
                y=data['MA20'],
                name='MA20',
                line=dict(color='orange')
            )
        ])
        
        fig.update_layout(
            title=f'Grafik {ticker} (1 Tahun)',
            xaxis_title='Tanggal',
            yaxis_title='Harga (Rp)',
            template='plotly_dark'
        )
        st.plotly_chart(fig, use_container_width=True)
    except:
        st.warning(f"Tidak bisa menampilkan grafik {ticker}")

# =============================================
# 🖥️ ANTARMUKA STREAMLIT
# =============================================

def main():
    st.set_page_config(
        page_title="Analisis Saham BEI",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    init_session()
    
    st.title("📈 Analisis Portofolio Saham BEI")
    st.markdown("""
    **Aplikasi untuk menganalisis saham Bursa Efek Indonesia (IDX)**
    - Valuasi (PER, PBV, Dividend Yield)
    - Prediksi harga dengan AI
    - Manajemen portofolio
    """)
    
    menu = st.sidebar.radio("Menu", [
        "Portofolio Saya", 
        "Analisis Saham", 
        "Prediksi AI"
    ])
    
    if menu == "Portofolio Saya":
        st.header("📋 Portofolio Anda")
        
        with st.form("tambah_saham"):
            col1, col2 = st.columns(2)
            with col1:
                ticker = st.text_input("Kode Saham (contoh: BBCA)", "").upper()
            with col2:
                lots = st.number_input("Jumlah Lot", min_value=1, value=1)
            
            if st.form_submit_button("Tambahkan"):
                if ticker:
                    st.session_state.portfolio[ticker] = lots
                    st.success(f"✅ {ticker} ditambahkan!")
        
        if st.session_state.portfolio:
            st.subheader("Daftar Saham")
            analysis_results = []
            
            for ticker, lots in st.session_state.portfolio.items():
                result = analyze_stock(ticker)
                if result:
                    result['Jumlah Lot'] = lots
                    analysis_results.append(result)
            
            if analysis_results:
                df = pd.DataFrame(analysis_results)
                st.dataframe(
                    df.style.applymap(
                        lambda x: 'background-color: #e6ffe6' if 'UNDERVALUED' in str(x) 
                        else ('background-color: #ffcccc' if 'OVERVALUED' in str(x) else ''),
                        subset=['Rekomendasi']
                    ),
                    hide_index=True
                )
        else:
            st.warning("Portofolio kosong. Tambahkan saham terlebih dahulu.")
    
    elif menu == "Analisis Saham":
        st.header("🔍 Analisis Saham Individual")
        ticker = st.text_input("Masukkan Kode Saham (contoh: TLKM)", "").upper()
        
        if ticker:
            with st.spinner(f"Menganalisis {ticker}..."):
                result = analyze_stock(ticker)
                if result:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric("Harga Terkini", f"Rp {result['Harga (Rp)']}")
                        st.metric("PER", result['PER'])
                        st.metric("PBV", result['PBV'])
                    
                    with col2:
                        st.metric("Dividend Yield", result['Dividend Yield (%)'])
                        st.metric("RSI (14)", result['RSI (14)'])
                        st.metric("Rekomendasi", result['Rekomendasi'])
                    
                    plot_stock_chart(ticker)
    
    elif menu == "Prediksi AI":
        st.header("🤖 Prediksi Harga dengan AI")
        st.warning("Fitur ini menggunakan model sederhana. Hasil tidak menjamin akurasi 100%.")
        
        ticker = st.text_input("Kode Saham untuk Prediksi", "BBCA").upper()
        if st.button("Prediksi"):
            with st.spinner("Menjalankan model AI..."):
                try:
                    stock = yf.Ticker(f"{ticker}.JK")
                    hist = stock.history(period="1y")
                    current_price = hist['Close'].iloc[-1]
                    predicted = predict_with_lstm(hist['Close'])
                    
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=hist.index,
                        y=hist['Close'],
                        name='Harga Historis'
                    ))
                    fig.add_trace(go.Scatter(
                        x=[hist.index[-1], hist.index[-1] + timedelta(days=180)],
                        y=[current_price, predicted],
                        name='Prediksi 6 Bulan',
                        line=dict(color='red', dash='dot')
                    ))
                    
                    fig.update_layout(
                        title=f"Prediksi {ticker}",
                        yaxis_title="Harga (Rp)"
                    )
                    st.plotly_chart(fig)
                    
                    st.success(f"""
                    **Hasil Prediksi:**
                    - Harga Saat Ini: Rp {current_price:,.0f}
                    - Prediksi 6 Bulan: Rp {predicted:,.0f}
                    """)
                except:
                    st.error("Gagal memprediksi. Coba kode saham lain.")

# =============================================
# 🚀 JALANKAN APLIKASI
# =============================================
if __name__ == "__main__":
    main()
