import streamlit as st
from config import Config
from views.dashboard_view import show_dashboard
from views.fundamental_view import show_fundamental_analysis
from views.technical_view import show_technical_analysis
from views.prediction_view import show_price_prediction
from views.portfolio_view import portfolio_simulation
from views.comparison_view import compare_stocks

def main():
    # Setup konfigurasi
    Config.setup()
    
    # UI Header
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
            show_dashboard(ticker)
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
