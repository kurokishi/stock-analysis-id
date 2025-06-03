import streamlit as st
from config import AppConfig
from core.data_provider import StockDataProvider
from views import DashboardView, AnalysisView, PredictionView
from core.portfolio import PortfolioAnalyzer
from views.portfolio import PortfolioView

# Dalam fungsi setup_app():
def setup_app():
    config = AppConfig()
    data_provider = StockDataProvider(config.cache_dir, config.cache_ttl)
    
    st.set_page_config(
        layout="wide", 
        page_title=config.app_title,
        page_icon="📊"
    )
    
    return {
        'config': config,
        'data_provider': data_provider,
        'dashboard_view': DashboardView(data_provider),
        'analysis_view': AnalysisView(data_provider),
        'prediction_view': PredictionView(data_provider),
        'portfolio_view' : PortfolioView(data_provider)
    }

def main():
    app = setup_app()
    
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
    
    tickers_input = st.sidebar.text_input(
        "Masukkan kode saham (pisahkan dengan koma)", 
        value=", ".join(app['config'].default_tickers)
    )
    tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]
    
    if not tickers:
        st.warning("Silakan masukkan minimal satu kode saham")
        return
    
    try:
        if app_mode == "Perbandingan Saham":
            # Ganti dengan method yang sesuai jika compare_stocks tidak ada
            if hasattr(app['dashboard_view'], 'compare_stocks'):
                app['dashboard_view'].compare_stocks(tickers)
            else:
                st.warning("Fitur perbandingan saham belum tersedia")
                app['dashboard_view'].show(tickers[0])  # Fallback ke tampilan default
        elif len(tickers) > 1:
            st.warning(f"Mode '{app_mode}' hanya tersedia untuk analisis satu saham")
            st.info("Sedang menampilkan Dashboard Utama untuk saham pertama")
            app['dashboard_view'].show(tickers[0])
        else:
            ticker = tickers[0]
            if app_mode == "Dashboard Utama":
                app['dashboard_view'].show(ticker)
            elif app_mode == "Analisis Fundamental":
                app['analysis_view'].show_fundamental(ticker)
            elif app_mode == "Analisis Teknikal":
                app['analysis_view'].show_technical(ticker)
            elif app_mode == "Prediksi Harga":
                app['prediction_view'].show(ticker)
            elif app_mode == "Simulasi Portofolio":
                app['dashboard_view'].show_portfolio_simulation(ticker)
    except Exception as e:
        st.error(f"Terjadi kesalahan: {str(e)}")
        st.info("Silakan coba lagi atau hubungi developer")

if __name__ == "__main__":
    main()
