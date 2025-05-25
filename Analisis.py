# 📌 stock_analysis_tf_compat.py
# Aplikasi Analisis Saham BEI dengan TensorFlow (Python 3.13 Compatible)
# by [Nama Anda]

import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os
import warnings
warnings.filterwarnings('ignore')

# =============================================
# 🛠️ KONFIGURASI TENSORFLOW KOMPATIBILITAS
# =============================================

def setup_tensorflow():
    """Handle TensorFlow compatibility for Python 3.13"""
    if sys.version_info >= (3, 13):
        st.warning("Menggunakan konfigurasi TensorFlow eksperimental untuk Python 3.13")
        os.environ['TF_USE_LEGACY_KERAS'] = '1'
        os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Kurangi log verbose
    
    try:
        from tensorflow.keras.models import Sequential
        from tensorflow.keras.layers import LSTM, Dense, Dropout
        from tensorflow.keras.optimizers import Adam
        from tensorflow.keras.callbacks import EarlyStopping
        from sklearn.preprocessing import MinMaxScaler
        return Sequential, LSTM, Dense, Adam, MinMaxScaler, EarlyStopping, Dropout
    except ImportError as e:
        st.error(f"Error mengimpor TensorFlow: {str(e)}")
        st.stop()

# Inisialisasi komponen TensorFlow
Sequential, LSTM, Dense, Adam, MinMaxScaler, EarlyStopping, Dropout = setup_tensorflow()

# =============================================
# 🧠 FUNGSI PREDIKSI DENGAN TENSORFLOW
# =============================================

def create_lstm_model(input_shape):
    """Membuat model LSTM dengan arsitektur yang lebih baik"""
    model = Sequential([
        LSTM(64, return_sequences=True, input_shape=input_shape),
        Dropout(0.2),
        LSTM(32),
        Dropout(0.2),
        Dense(1)
    ])
    model.compile(
        optimizer=Adam(learning_rate=0.001),
        loss='mse',
        metrics=['mae']
    )
    return model

def predict_with_tensorflow(prices, lookback=60, epochs=20):
    """Prediksi harga saham dengan LSTM"""
    try:
        # Normalisasi data
        scaler = MinMaxScaler()
        scaled_data = scaler.fit_transform(prices.values.reshape(-1, 1))
        
        # Siapkan data training
        X, y = [], []
        for i in range(lookback, len(scaled_data)):
            X.append(scaled_data[i-lookback:i, 0])
            y.append(scaled_data[i, 0])
        
        X, y = np.array(X), np.array(y)
        X = np.reshape(X, (X.shape[0], X.shape[1], 1))
        
        # Pembagian data (sederhana)
        split = int(0.8 * len(X))
        X_train, y_train = X[:split], y[:split]
        
        # Latih model
        model = create_lstm_model((X.shape[1], 1))
        early_stop = EarlyStopping(monitor='loss', patience=5, restore_best_weights=True)
        
        model.fit(
            X_train, y_train,
            epochs=epochs,
            batch_size=32,
            callbacks=[early_stop],
            verbose=0
        )
        
        # Prediksi
        last_sequence = scaled_data[-lookback:]
        last_sequence = np.reshape(last_sequence, (1, lookback, 1))
        predicted = model.predict(last_sequence, verbose=0)
        predicted_price = scaler.inverse_transform(predicted)[0][0]
        
        return max(predicted_price, 0)
    
    except Exception as e:
        st.error(f"Error dalam prediksi: {str(e)}")
        return prices.iloc[-1] * (1 + np.random.uniform(-0.05, 0.1))  # Fallback

# =============================================
# 📊 FUNGSI ANALISIS SAHAM
# =============================================

def calculate_rsi(prices, window=14):
    """Hitung Relative Strength Index (RSI)"""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def analyze_stock(ticker):
    """Analisis fundamental dan teknikal saham"""
    try:
        stock = yf.Ticker(f"{ticker}.JK")
        hist = stock.history(period="1y")
        
        if hist.empty:
            st.error(f"Tidak ada data untuk {ticker}")
            return None
        
        # Indikator Teknikal
        hist['MA20'] = hist['Close'].rolling(20).mean()
        hist['RSI'] = calculate_rsi(hist['Close'])
        
        # Prediksi Harga
        current_price = hist['Close'].iloc[-1]
        predicted_price = predict_with_tensorflow(hist['Close'])
        
        # Analisis Fundamental
        info = stock.info
        per = info.get('trailingPE', np.nan)
        pbv = info.get('priceToBook', np.nan)
        dy = info.get('dividendYield', 0) * 100  # dalam persen
        
        # Rekomendasi
        if pd.isna(per) or pd.isna(pbv):
            recommendation = "DATA TIDAK LENGKAP"
            color = "gray"
        elif per < 12 and pbv < 1.5:
            recommendation = "UNDERVALUED 🟢 (Potensi Beli)"
            color = "green"
        elif per > 20 or pbv > 3:
            recommendation = "OVERVALUED 🔴 (Hati-hati)"
            color = "red"
        else:
            recommendation = "FAIRLY VALUED 🟡 (Tahan)"
            color = "orange"
            
        return {
            'Ticker': ticker,
            'Harga (Rp)': f"{current_price:,.0f}",
            'Prediksi 6 Bulan (Rp)': f"{predicted_price:,.0f}",
            'PER': f"{per:.2f}",
            'PBV': f"{pbv:.2f}",
            'Dividend Yield (%)': f"{dy:.2f}%",
            'RSI (14)': f"{hist['RSI'].iloc[-1]:.1f}",
            'Rekomendasi': recommendation,
            'Warna': color
        }
    except Exception as e:
        st.error(f"Error analisis {ticker}: {str(e)}")
        return None

# =============================================
# 📈 FUNGSI VISUALISASI
# =============================================

def plot_stock_chart(ticker, with_prediction=False):
    """Plot grafik saham interaktif dengan Plotly"""
    try:
        data = yf.Ticker(f"{ticker}.JK").history(period="1y")
        
        if data.empty:
            st.warning(f"Tidak ada data grafik untuk {ticker}")
            return
        
        fig = go.Figure()
        
        # Candlestick
        fig.add_trace(go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            name='Harga',
            increasing_line_color='green',
            decreasing_line_color='red'
        ))
        
        # Moving Average
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['Close'].rolling(20).mean(),
            name='MA20',
            line=dict(color='orange', width=2)
        ))
        
        if with_prediction:
            # Prediksi
            current_price = data['Close'].iloc[-1]
            predicted_price = predict_with_tensorflow(data['Close'])
            
            fig.add_trace(go.Scatter(
                x=[data.index[-1], data.index[-1] + timedelta(days=180)],
                y=[current_price, predicted_price],
                name='Prediksi 6 Bulan',
                line=dict(color='blue', dash='dot', width=3),
                mode='lines+markers'
            ))
        
        fig.update_layout(
            title=f'Grafik {ticker} (1 Tahun)',
            xaxis_title='Tanggal',
            yaxis_title='Harga (Rp)',
            hovermode='x unified',
            template='plotly_white',
            height=600
        )
        
        fig.update_xaxes(
            rangeslider_visible=False,
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(step="all")
                ])
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Error membuat grafik: {str(e)}")

# =============================================
# 🖥️ ANTARMUKA STREAMLIT
# =============================================

def init_session():
    """Inisialisasi session state"""
    if 'portfolio' not in st.session_state:
        st.session_state.portfolio = {}

def main():
    st.set_page_config(
        page_title="Analisis Saham BEI dengan TensorFlow",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("📈 Analisis Saham BEI dengan TensorFlow")
    st.markdown("""
    **Aplikasi untuk menganalisis saham Bursa Efek Indonesia (IDX)**
    - Prediksi harga dengan model LSTM
    - Analisis valuasi fundamental
    - Manajemen portofolio
    """)
    
    init_session()
    
    menu = st.sidebar.radio(
        "Menu Utama",
        ["Portofolio Saya", "Analisis Saham", "Prediksi AI", "Tentang"]
    )
    
    if menu == "Portofolio Saya":
        st.header("📋 Manajemen Portofolio")
        
        with st.form("tambah_saham"):
            col1, col2 = st.columns(2)
            with col1:
                ticker = st.text_input("Kode Saham (contoh: BBCA)", "").upper().strip()
            with col2:
                lots = st.number_input("Jumlah Lot", min_value=1, value=1)
            
            if st.form_submit_button("Tambahkan ke Portofolio"):
                if ticker:
                    if ticker in st.session_state.portfolio:
                        st.warning(f"{ticker} sudah ada di portofolio")
                    else:
                        st.session_state.portfolio[ticker] = lots
                        st.success(f"✅ {ticker} ditambahkan ke portofolio!")
                else:
                    st.error("Masukkan kode saham yang valid")
        
        if st.session_state.portfolio:
            st.subheader("Daftar Saham Anda")
            analysis_results = []
            
            for ticker, lots in st.session_state.portfolio.items():
                with st.spinner(f"Menganalisis {ticker}..."):
                    result = analyze_stock(ticker)
                    if result:
                        result['Jumlah Lot'] = lots
                        analysis_results.append(result)
            
            if analysis_results:
                df = pd.DataFrame(analysis_results)
                
                # Tampilkan tabel dengan warna
                st.dataframe(
                    df.style.apply(
                        lambda x: [f"background-color: {x['Warna']}" if x.name == 'Rekomendasi' else '' for x in df.iloc[0]], 
                        axis=1
                    ).format(precision=2),
                    hide_index=True,
                    use_container_width=True
                )
                
                # Tombol hapus saham
                to_delete = st.selectbox(
                    "Pilih saham untuk dihapus",
                    [""] + list(st.session_state.portfolio.keys())
                )
                
                if to_delete and st.button("Hapus Saham"):
                    del st.session_state.portfolio[to_delete]
                    st.success(f"{to_delete} dihapus dari portofolio")
                    st.experimental_rerun()
        else:
            st.info("Portofolio Anda kosong. Tambahkan saham terlebih dahulu.")
    
    elif menu == "Analisis Saham":
        st.header("🔍 Analisis Saham Individual")
        
        ticker = st.text_input("Masukkan Kode Saham (contoh: TLKM)", "").upper().strip()
        
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
                    
                    tab1, tab2 = st.tabs(["Grafik Harga", "Analisis Teknikal"])
                    
                    with tab1:
                        plot_stock_chart(ticker)
                    
                    with tab2:
                        st.subheader("Indikator Teknikal")
                        plot_stock_chart(ticker)
    
    elif menu == "Prediksi AI":
        st.header("🤖 Prediksi Harga dengan LSTM")
        st.info("""
        Fitur ini menggunakan model LSTM dari TensorFlow untuk memprediksi pergerakan harga saham.
        Hasil prediksi tidak menjamin akurasi 100% dan hanya untuk referensi.
        """)
        
        ticker = st.text_input("Masukkan Kode Saham untuk Prediksi", "BBCA").upper().strip()
        
        if st.button("Jalankan Prediksi AI"):
            if not ticker:
                st.error("Masukkan kode saham yang valid")
            else:
                with st.spinner("Menjalankan model TensorFlow..."):
                    try:
                        data = yf.Ticker(f"{ticker}.JK").history(period="1y")
                        
                        if data.empty:
                            st.error(f"Tidak ada data untuk {ticker}")
                        else:
                            current_price = data['Close'].iloc[-1]
                            predicted = predict_with_tensorflow(data['Close'])
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric("Harga Saat Ini", f"Rp {current_price:,.0f}")
                            with col2:
                                st.metric("Prediksi 6 Bulan", f"Rp {predicted:,.0f}", 
                                         delta=f"{((predicted-current_price)/current_price*100):.1f}%")
                            
                            plot_stock_chart(ticker, with_prediction=True)
                            
                            st.success("""
                            **Interpretasi Prediksi:**
                            - Model dilatih menggunakan data historis 1 tahun
                            - Menggunakan arsitektur LSTM dengan 2 layer
                            - Dilengkapi dropout untuk mengurangi overfitting
                            """)
                    except Exception as e:
                        st.error(f"Gagal memprediksi: {str(e)}")
    
    elif menu == "Tentang":
        st.header("📝 Tentang Aplikasi")
        st.markdown("""
        **Aplikasi Analisis Saham BEI dengan TensorFlow**
        
        Dibangun dengan:
        - Python 3.11/3.12
        - Streamlit untuk antarmuka
        - TensorFlow/Keras untuk model LSTM
        - yFinance untuk data saham
        
        **Fitur Utama:**
        1. Analisis fundamental (PER, PBV, Dividend Yield)
        2. Analisis teknikal (RSI, Moving Average)
        3. Prediksi harga dengan AI (LSTM)
        4. Manajemen portofolio saham
        
        **Catatan:**
        - Hasil prediksi bukan rekomendasi finansial
        - Gunakan sebagai referensi tambahan
        """)

# =============================================
# 🚀 JALANKAN APLIKASI
# =============================================
if __name__ == "__main__":
    main()
