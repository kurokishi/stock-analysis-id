# main.py
import streamlit as st
from config import Config
from views import (
    show_dashboard,
    show_fundamental_analysis,
    show_technical_analysis,
    show_price_prediction,
    portfolio_simulation,
    compare_stocks
)

def main():
    Config.setup()
    
    st.title("📊 Analisis Saham Lengkap + AI Prediksi")
    
    # Sidebar navigation
    st.sidebar.title("Menu")
    app_mode = st.sidebar.radio(
        "Pilih Analisis", 
        [
            "Dashboard Utama", 
            "Analisis Fundamental", 
            "Analisis Teknikal", 
            "Prediksi Harga", 
            "Simulasi Portofolio", 
            "Perbandingan Saham"
        ]
    )
    
    # Input ticker
    tickers_input = st.sidebar.text_input(
        "Masukkan kode saham (pisahkan dengan koma)", 
        value=",".join(Config.DEFAULT_TICKERS)
    )
    tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]
    
    if not tickers:
        st.warning("Silakan masukkan minimal satu kode saham")
        return
    
    # Routing berdasarkan mode
    if app_mode == "Perbandingan Saham":
        compare_stocks(tickers)
    elif len(tickers) > 1:
        st.warning(f"Mode '{app_mode}' hanya tersedia untuk analisis satu saham")
        st.info("Sedang menampilkan mode Perbandingan Saham sebagai gantinya")
        compare_stocks(tickers)
    else:
        ticker = tickers[0]
        if app_mode == "Dashboard Utama":
            show_dashboard(ticker)  # Panggil dengan parameter ticker
        elif app_mode == "Analisis Fundamental":
            show_fundamental_analysis(ticker)
        elif app_mode == "Analisis Teknikal":
            show_technical_analysis(ticker)
        elif app_mode == "Prediksi Harga":
            show_price_prediction(ticker)
        elif app_mode == "Simulasi Portofolio":
            portfolio_simulation(ticker)

if __name__ == "__main__":
    main()
