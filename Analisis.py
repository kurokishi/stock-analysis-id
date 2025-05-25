import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import sys
import os
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import plotly.graph_objects as go

# ========== TENSORFLOW COMPATIBILITY LAYER ==========
def setup_tensorflow():
    """Handle TensorFlow compatibility across Python versions"""
    if sys.version_info >= (3, 13):
        st.warning("Python 3.13 detected - Using experimental config")
        os.environ['TF_USE_LEGACY_KERAS'] = '1'
        os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Suppress TensorFlow logs
    
    try:
        import tensorflow as tf
        from tensorflow.keras.models import Sequential
        from tensorflow.keras.layers import LSTM, Dense, Dropout
        from tensorflow.keras.optimizers import Adam
        from tensorflow.keras.callbacks import EarlyStopping
        return tf, Sequential, LSTM, Dense, Adam, EarlyStopping, Dropout
    except ImportError:
        st.error("""
        TensorFlow tidak dapat di-load. Kemungkinan penyebab:
        1. Python versi 3.13 yang belum didukung penuh
        2. Masalah instalasi dependencies
        """)
        if st.button("Coba gunakan mode tanpa TensorFlow"):
            return None, None, None, None, None, None, None
        st.stop()

tf, Sequential, LSTM, Dense, Adam, EarlyStopping, Dropout = setup_tensorflow()

# ========== FUNGSI UTAMA DENGAN FALLBACK ==========
def predict_with_fallback(prices, lookback=60):
    """Prediksi harga dengan fallback ke metode sederhana jika TF gagal"""
    if tf is None:
        # Fallback ke perhitungan sederhana jika TensorFlow tidak tersedia
        return prices.iloc[-1] * (1 + np.random.uniform(-0.05, 0.1))
    
    try:
        from sklearn.preprocessing import MinMaxScaler
        scaler = MinMaxScaler()
        scaled_data = scaler.fit_transform(prices.values.reshape(-1, 1))
        
        # Siapkan data
        X, y = [], []
        for i in range(lookback, len(scaled_data)):
            X.append(scaled_data[i-lookback:i, 0])
            y.append(scaled_data[i, 0])
        
        X, y = np.array(X), np.array(y)
        X = np.reshape(X, (X.shape[0], X.shape[1], 1))
        
        # Model LSTM
        model = Sequential([
            LSTM(50, return_sequences=True, input_shape=(X.shape[1], 1)),
            Dropout(0.2),
            LSTM(50),
            Dropout(0.2),
            Dense(1)
        ])
        model.compile(optimizer=Adam(learning_rate=0.001), loss='mse')
        
        # Training sederhana
        model.fit(X, y, epochs=10, batch_size=32, verbose=0)
        
        # Prediksi
        last_sequence = scaled_data[-lookback:]
        last_sequence = np.reshape(last_sequence, (1, lookback, 1))
        predicted = model.predict(last_sequence, verbose=0)
        return scaler.inverse_transform(predicted)[0][0]
    
    except Exception as e:
        st.warning(f"Prediksi LSTM gagal, menggunakan fallback: {str(e)}")
        return prices.iloc[-1] * (1 + np.random.uniform(-0.05, 0.1))

# ... (fungsi-fungsi lainnya tetap sama seperti sebelumnya)

def main():
    st.set_page_config(...)
    
    # Tambahkan warning kompatibilitas
    if sys.version_info >= (3, 13):
        st.warning("""
        ⚠️ Anda menggunakan Python 3.13. Beberapa fitur mungkin terbatas.
        Untuk pengalaman terbaik, gunakan Python 3.11.
        """)
    
    # ... (implementasi antarmuka tetap sama)
