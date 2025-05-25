# 📌 stock_analysis_tf.py
# Aplikasi Analisis Saham BEI dengan TensorFlow
# by [Nama Anda]

import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from datetime import datetime, timedelta
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
import warnings
warnings.filterwarnings('ignore')

# =============================================
# 🛠️ FUNGSI UTAMA DENGAN TENSORFLOW
# =============================================

def init_session():
    """Inisialisasi session state"""
    if 'portfolio' not in st.session_state:
        st.session_state.portfolio = {}

def check_python_version():
    """Pastikan versi Python kompatibel"""
    import sys
    if sys.version_info >= (3, 13):
        st.error("⚠️ Python 3.13 tidak didukung TensorFlow. Gunakan Python 3.9-3.11")
        st.stop()

def prepare_lstm_model(input_shape):
    """Membuat model LSTM sederhana"""
    model = Sequential([
        LSTM(50, return_sequences=True, input_shape=input_shape),
        LSTM(50),
        Dense(1)
    ])
    model.compile(optimizer='adam', loss='mse')
    return model

def predict_with_tensorflow(prices, lookback=60):
    """Prediksi harga dengan TensorFlow LSTM"""
    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(prices.values.reshape(-1, 1))
    
    # Siapkan data training (dummy)
    X_train, y_train = [], []
    for i in range(lookback, len(scaled_data)):
        X_train.append(scaled_data[i-lookback:i, 0])
        y_train.append(scaled_data[i, 0])
    
    X_train, y_train = np.array(X_train), np.array(y_train)
    X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))
    
    # Buat dan latih model
    model = prepare_lstm_model((X_train.shape[1], 1))
    model.fit(X_train, y_train, epochs=10, batch_size=32, verbose=0)
    
    # Prediksi
    inputs = scaled_data[-lookback:].reshape(1, lookback, 1)
    predicted = model.predict(inputs, verbose=0)
    predicted_price = scaler.inverse_transform(predicted)[0][0]
    
    return max(predicted_price, 0)  # Harga tidak boleh negatif

def analyze_stock(ticker):
    """Analisis saham dengan TensorFlow"""
    try:
        stock = yf.Ticker(f"{ticker}.JK")
        hist = stock.history(period="1y")
        
        # Perhitungan indikator
        hist['MA20'] = hist['Close'].rolling(20).mean()
        hist['RSI'] = calculate_rsi(hist['Close'])
        
        # Prediksi harga dengan TensorFlow
        current_price = hist['Close'].iloc[-1]
        predicted_price = predict_with_tensorflow(hist['Close'])
        
        # Valuasi
        info = stock.info
        per = info.get('trailingPE', np.nan)
        pbv = info.get('priceToBook', np.nan)
        dy = info.get('dividendYield', 0) * 100  # dalam persen
        
        # Rekomendasi
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

# =============================================
# 🖥️ ANTARMUKA STREAMLIT
# =============================================

def main():
    st.set_page_config(
        page_title="Analisis Saham BEI dengan TensorFlow",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    check_python_version()
    init_session()
    
    st.title("📈 Analisis Saham BEI dengan TensorFlow")
    st.markdown("""
    **Aplikasi untuk menganalisis saham Bursa Efek Indonesia (IDX)**
    - Prediksi harga dengan model LSTM
    - Analisis valuasi fundamental
    - Manajemen portofolio
    """)
    
    menu = st.sidebar.radio("Menu", [
        "Portofolio Saya", 
        "Analisis Saham", 
        "Prediksi TensorFlow"
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
            with st.spinner(f"Menganalisis {ticker} dengan TensorFlow..."):
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
    
    elif menu == "Prediksi TensorFlow":
        st.header("🤖 Prediksi Harga dengan TensorFlow LSTM")
        st.info("Fitur ini menggunakan model LSTM untuk prediksi harga saham")
        
        ticker = st.text_input("Kode Saham untuk Prediksi", "BBCA").upper()
        if st.button("Jalankan Prediksi"):
            with st.spinner("Menjalankan model TensorFlow..."):
                try:
                    stock = yf.Ticker(f"{ticker}.JK")
                    hist = stock.history(period="1y")
                    current_price = hist['Close'].iloc[-1]
                    predicted = predict_with_tensorflow(hist['Close'])
                    
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
                        title=f"Prediksi {ticker} dengan LSTM",
                        yaxis_title="Harga (Rp)"
                    )
                    st.plotly_chart(fig)
                    
                    st.success(f"""
                    **Hasil Prediksi TensorFlow:**
                    - Harga Saat Ini: Rp {current_price:,.0f}
                    - Prediksi 6 Bulan: Rp {predicted:,.0f}
                    - Perubahan: {((predicted-current_price)/current_price*100):.1f}%
                    """)
                except Exception as e:
                    st.error(f"Gagal memprediksi: {str(e)}")

# =============================================
# 🛠️ FUNGSI PENDUKUNG
# =============================================

def calculate_rsi(prices, window=14):
    """Hitung Relative Strength Index (RSI)"""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

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
                y=data['Close'].rolling(20).mean(),
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
# 🚀 JALANKAN APLIKASI
# =============================================
if __name__ == "__main__":
    main()
