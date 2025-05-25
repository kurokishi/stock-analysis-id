import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
import requests
from bs4 import BeautifulSoup
import ta
import warnings
warnings.filterwarnings('ignore')

# Konfigurasi awal
st.set_page_config(layout="wide", page_title="Enhanced Portfolio Analyzer")

# Fungsi untuk mendapatkan data saham dengan error handling
def get_stock_data(ticker, period='1y'):
    try:
        stock = yf.Ticker(ticker + ".JK")
        hist = stock.history(period=period)
        if hist.empty:
            st.warning(f"Tidak ada data historis untuk {ticker}")
            return None, None
        return stock, hist
    except Exception as e:
        st.error(f"Error mendapatkan data untuk {ticker}: {str(e)}")
        return None, None

# Fungsi untuk menghitung indikator teknikal lengkap
def calculate_technical_indicators(df):
    if df is None or df.empty:
        return None
    
    try:
        # Moving Averages
        df['MA20'] = df['Close'].rolling(window=20).mean()
        df['MA50'] = df['Close'].rolling(window=50).mean()
        df['MA100'] = df['Close'].rolling(window=100).mean()
        df['MA200'] = df['Close'].rolling(window=200).mean()
        
        # RSI
        df['RSI14'] = ta.RSI(df['Close'], timeperiod=14)
        
        # MACD
        df['MACD'], df['MACD_Signal'], df['MACD_Hist'] = ta.MACD(
            df['Close'], fastperiod=12, slowperiod=26, signalperiod=9)
        
        # Bollinger Bands
        df['UpperBand'], df['MiddleBand'], df['LowerBand'] = ta.BBANDS(
            df['Close'], timeperiod=20)
        
        # Stochastic Oscillator
        df['SlowK'], df['SlowD'] = ta.STOCH(
            df['High'], df['Low'], df['Close'],
            fastk_period=14, slowk_period=3, slowd_period=3)
        
        # Volume Weighted Average Price
        df['VWAP'] = (df['Volume'] * (df['High'] + df['Low'] + df['Close']) / 3).cumsum() / df['Volume'].cumsum()
        
        # Average True Range
        df['ATR'] = ta.ATR(df['High'], df['Low'], df['Close'], timeperiod=14)
        
        return df.dropna()
    except Exception as e:
        st.error(f"Error menghitung indikator teknikal: {str(e)}")
        return None

# Fungsi untuk mendapatkan data fundamental dengan error handling
def get_fundamental_data(ticker):
    fundamental = {
        'PER': np.nan,
        'PBV': np.nan,
        'Dividend Yield': np.nan,
        'ROE': np.nan,
        'DER': np.nan,
        'EPS': np.nan,
        'Market Cap': np.nan,
        'Beta': np.nan
    }
    
    try:
        stock = yf.Ticker(ticker + ".JK")
        info = stock.info
        
        fundamental['PER'] = info.get('trailingPE', np.nan)
        fundamental['PBV'] = info.get('priceToBook', np.nan)
        fundamental['Dividend Yield'] = info.get('dividendYield', np.nan) or np.nan
        fundamental['ROE'] = info.get('returnOnEquity', np.nan)
        fundamental['DER'] = info.get('debtToEquity', np.nan)
        fundamental['EPS'] = info.get('trailingEps', np.nan)
        fundamental['Market Cap'] = info.get('marketCap', np.nan)
        fundamental['Beta'] = info.get('beta', np.nan)
        
        # Scrape additional data from IDX (simulated)
        try:
            url = f"https://www.idx.co.id/PerusahaanTercatat/ProfilPerusahaanTercatat/{ticker}"
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                # Simulated scraping - in reality would parse actual elements
                fundamental['Shares Outstanding'] = np.nan  # Would extract from page
        except:
            pass
        
    except Exception as e:
        st.error(f"Error mendapatkan data fundamental untuk {ticker}: {str(e)}")
    
    return fundamental

# Fungsi untuk mengevaluasi valuasi yang lebih komprehensif
def evaluate_valuation(fundamental):
    if not fundamental or all(pd.isna(v) for v in fundamental.values()):
        return "Data tidak tersedia", {}
    
    scores = {}
    valuation = "Fairly valued"
    
    # PER evaluation
    if not pd.isna(fundamental['PER']):
        if fundamental['PER'] < 10:
            scores['PER'] = 2
        elif fundamental['PER'] < 15:
            scores['PER'] = 1
        else:
            scores['PER'] = 0
    
    # PBV evaluation
    if not pd.isna(fundamental['PBV']):
        if fundamental['PBV'] < 1:
            scores['PBV'] = 2
        elif fundamental['PBV'] < 2:
            scores['PBV'] = 1
        else:
            scores['PBV'] = 0
    
    # Dividend Yield evaluation
    if not pd.isna(fundamental['Dividend Yield']):
        if fundamental['Dividend Yield'] > 0.05:  # 5%
            scores['DY'] = 2
        elif fundamental['Dividend Yield'] > 0.03:  # 3%
            scores['DY'] = 1
        else:
            scores['DY'] = 0
    
    # ROE evaluation
    if not pd.isna(fundamental['ROE']):
        if fundamental['ROE'] > 0.15:  # 15%
            scores['ROE'] = 1
        else:
            scores['ROE'] = 0
    
    # Calculate total score
    total_score = sum(scores.values())
    
    if total_score >= 5:
        valuation = "Strongly Undervalued"
    elif total_score >= 3:
        valuation = "Undervalued"
    elif total_score <= 1:
        valuation = "Overvalued"
    
    return valuation, scores

# Fungsi untuk proyeksi dividen dengan error handling
def calculate_dividend_projection(ticker, shares, current_price):
    try:
        stock = yf.Ticker(ticker + ".JK")
        dividends = stock.dividends
        
        if len(dividends) > 0:
            # Use average of last 3 years dividends
            avg_dividend = dividends.last('3Y').mean()
            dividend_per_share = avg_dividend
            annual_dividend = shares * dividend_per_share
            return annual_dividend
        return 0
    except Exception as e:
        st.error(f"Error menghitung proyeksi dividen untuk {ticker}: {str(e)}")
        return 0

# Fungsi untuk simulasi bunga majemuk
def compound_interest_simulation(initial_value, growth_rate, years, dividend_yield=0, reinvest=True):
    results = []
    current_value = initial_value
    
    for year in range(1, years+1):
        try:
            capital_growth = current_value * (1 + growth_rate)
            dividends = current_value * dividend_yield
            
            if reinvest:
                current_value = capital_growth + dividends
            else:
                current_value = capital_growth
            
            results.append({
                'Year': year,
                'Portfolio Value': current_value,
                'Capital Growth': capital_growth,
                'Dividends': dividends if not reinvest else 0
            })
        except Exception as e:
            st.error(f"Error dalam simulasi tahun {year}: {str(e)}")
            break
    
    return pd.DataFrame(results)

# Inisialisasi session state untuk portofolio
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = pd.DataFrame(columns=[
        'Ticker', 'Shares', 'Buy Price', 'Current Price', 'Value', 
        'Last Updated'
    ])

# UI Aplikasi
st.title("📈 Enhanced Stock Portfolio Analyzer")
st.markdown("""
**Aplikasi analisis portofolio saham dengan indikator teknikal & fundamental lengkap**  
Fitur utama:
- Analisis fundamental komprehensif (PER, PBV, ROE, DER, Dividend Yield)
- Indikator teknikal lengkap (MACD, RSI, Bollinger Bands, Stochastic, ATR)
- Rekomendasi alokasi berbasis AI
- Simulasi pertumbuhan portofolio
""")

# Tab navigasi
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Portofolio", 
    "Analisis Saham", 
    "Alokasi Modal", 
    "Rekomendasi", 
    "Simulasi"
])

with tab1:
    st.header("📊 Manajemen Portofolio")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Tambah/Edit Saham")
        with st.form("portfolio_form", clear_on_submit=True):
            ticker = st.text_input("Kode Saham (contoh: BBCA)", "").upper()
            shares = st.number_input("Jumlah Lot", min_value=1, value=1)
            buy_price = st.number_input("Harga Beli per Saham (Rp)", min_value=1, value=1000)
            
            submitted = st.form_submit_button("Tambahkan/Update")
            if submitted and ticker:
                try:
                    stock, hist = get_stock_data(ticker, '1d')
                    if stock and not hist.empty:
                        current_price = hist['Close'].iloc[-1]
                        
                        new_row = {
                            'Ticker': ticker,
                            'Shares': shares * 100,  # Convert lot to shares
                            'Buy Price': buy_price,
                            'Current Price': current_price,
                            'Value': shares * 100 * current_price,
                            'Last Updated': datetime.now().strftime("%Y-%m-%d %H:%M")
                        }
                        
                        if ticker in st.session_state.portfolio['Ticker'].values:
                            idx = st.session_state.portfolio.index[
                                st.session_state.portfolio['Ticker'] == ticker].tolist()[0]
                            st.session_state.portfolio.loc[idx] = new_row
                        else:
                            st.session_state.portfolio = pd.concat([
                                st.session_state.portfolio, 
                                pd.DataFrame([new_row])
                            ], ignore_index=True)
                        
                        st.success(f"{ticker} berhasil ditambahkan/diperbarui!")
                except Exception as e:
                    st.error(f"Gagal memproses {ticker}: {str(e)}")
    
    with col2:
        st.subheader("Hapus Saham")
        if not st.session_state.portfolio.empty:
            to_delete = st.selectbox(
                "Pilih saham untuk dihapus",
                st.session_state.portfolio['Ticker'].unique(),
                key="delete_select"
            )
            if st.button("Hapus dari Portofolio", key="delete_btn"):
                st.session_state.portfolio = st.session_state.portfolio[
                    st.session_state.portfolio['Ticker'] != to_delete]
                st.success(f"{to_delete} berhasil dihapus!")
        else:
            st.info("Portofolio kosong. Tambahkan saham terlebih dahulu.")
    
    st.subheader("Ringkasan Portofolio")
    if not st.session_state.portfolio.empty:
        # Hitung total nilai portofolio
        total_value = st.session_state.portfolio['Value'].sum()
        total_investment = (st.session_state.portfolio['Shares'] * 
                           st.session_state.portfolio['Buy Price']).sum()
        profit_loss = total_value - total_investment
        profit_loss_pct = (profit_loss / total_investment) * 100 if total_investment != 0 else 0
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Nilai Portofolio", f"Rp{total_value:,.0f}")
        col2.metric("Total Investasi", f"Rp{total_investment:,.0f}")
        col3.metric("Profit/Loss", 
                   f"Rp{profit_loss:,.0f}", 
                   f"{profit_loss_pct:.2f}%",
                   delta_color="inverse" if profit_loss < 0 else "normal")
        
        # Tampilkan tabel portofolio dengan format yang lebih baik
        display_cols = ['Ticker', 'Shares', 'Buy Price', 'Current Price', 'Value', 'Last Updated']
        st.dataframe(
            st.session_state.portfolio[display_cols].style.format({
                'Buy Price': 'Rp{:,.0f}',
                'Current Price': 'Rp{:,.0f}',
                'Value': 'Rp{:,.0f}'
            }),
            height=400,
            use_container_width=True
        )
        
        # Grafik alokasi portofolio
        fig = px.pie(
            st.session_state.portfolio, 
            names='Ticker', 
            values='Value',
            title='Alokasi Portofolio',
            hole=0.3
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Tombol refresh semua harga
        if st.button("Refresh Semua Harga"):
            with st.spinner("Memperbarui harga..."):
                updated_rows = []
                for _, row in st.session_state.portfolio.iterrows():
                    try:
                        _, hist = get_stock_data(row['Ticker'], '1d')
                        if hist is not None and not hist.empty:
                            new_price = hist['Close'].iloc[-1]
                            updated_row = row.copy()
                            updated_row['Current Price'] = new_price
                            updated_row['Value'] = row['Shares'] * new_price
                            updated_row['Last Updated'] = datetime.now().strftime("%Y-%m-%d %H:%M")
                            updated_rows.append(updated_row)
                    except:
                        continue
                
                if updated_rows:
                    st.session_state.portfolio = pd.DataFrame(updated_rows)
                    st.success("Harga berhasil diperbarui!")
                else:
                    st.error("Gagal memperbarui harga")
    else:
        st.info("Portofolio Anda masih kosong. Tambahkan saham untuk memulai analisis.")

with tab2:
    st.header("🔍 Analisis Saham Mendalam")
    
    if not st.session_state.portfolio.empty:
        selected_ticker = st.selectbox(
            "Pilih saham untuk dianalisis",
            st.session_state.portfolio['Ticker'].unique(),
            key="analysis_select"
        )
        
        stock_data = st.session_state.portfolio[
            st.session_state.portfolio['Ticker'] == selected_ticker].iloc[0]
        shares = stock_data['Shares']
        buy_price = stock_data['Buy Price']
        current_price = stock_data['Current Price']
        
        # Dapatkan data historis
        stock, hist = get_stock_data(selected_ticker, '1y')
        if hist is not None:
            hist = calculate_technical_indicators(hist)
            
            # Dapatkan data fundamental
            fundamental = get_fundamental_data(selected_ticker)
            valuation_status, valuation_scores = evaluate_valuation(fundamental)
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.subheader("Fundamental Analysis")
                
                # Tampilkan metrik fundamental
                st.metric("PER", f"{fundamental['PER']:.2f}" if not pd.isna(fundamental['PER']) else "N/A",
                         help="Price-to-Earnings Ratio")
                st.metric("PBV", f"{fundamental['PBV']:.2f}" if not pd.isna(fundamental['PBV']) else "N/A",
                         help="Price-to-Book Value")
                st.metric("Dividend Yield", f"{fundamental['Dividend Yield']:.2%}" if not pd.isna(fundamental['Dividend Yield']) else "N/A")
                st.metric("ROE", f"{fundamental['ROE']:.2%}" if not pd.isna(fundamental['ROE']) else "N/A",
                         help="Return on Equity")
                st.metric("DER", f"{fundamental['DER']:.2f}" if not pd.isna(fundamental['DER']) else "N/A",
                         help="Debt-to-Equity Ratio")
                st.metric("Market Cap", f"Rp{fundamental['Market Cap']:,.0f}" if not pd.isna(fundamental['Market Cap']) else "N/A")
                
                st.subheader("Valuation")
                st.metric("Status", valuation_status)
                
                # Tampilkan skor valuasi
                st.write("**Valuation Scores:**")
                for metric, score in valuation_scores.items():
                    st.progress(score/2, text=f"{metric}: {score}/2")
                
                # Analisis AI sederhana
                st.subheader("Analisis")
                if valuation_status == "Strongly Undervalued":
                    st.success("""
                    **Potensi Sangat Baik**: 
                    - Saham sangat undervalued berdasarkan berbagai metrik fundamental
                    - Memiliki margin of safety yang besar
                    - Pertimbangkan untuk menambah posisi
                    """)
                elif valuation_status == "Undervalued":
                    st.success("""
                    **Potensi Baik**:
                    - Saham undervalued berdasarkan beberapa metrik
                    - Memiliki ruang untuk apresiasi harga
                    - Pertimbangkan untuk hold atau tambah secara bertahap
                    """)
                elif valuation_status == "Overvalued":
                    st.warning("""
                    **Hati-hati**:
                    - Saham tampak overvalued
                    - Pertimbangkan untuk take profit atau cari peluang lain
                    - Pantau tanda-tanda koreksi
                    """)
                else:
                    st.info("""
                    **Netral**:
                    - Saham fairly valued
                    - Pantau perkembangan perusahaan
                    - Pertimbangkan faktor eksternal sebelum mengambil keputusan
                    """)
            
            with col2:
                st.subheader("Technical Analysis")
                
                # Tab untuk berbagai grafik teknikal
                tab_tech1, tab_tech2, tab_tech3, tab_tech4 = st.tabs([
                    "Price & MA", 
                    "RSI & MACD", 
                    "Bollinger Bands", 
                    "Stochastic"
                ])
                
                with tab_tech1:
                    fig = go.Figure()
                    fig.add_trace(go.Candlestick(
                        x=hist.index,
                        open=hist['Open'],
                        high=hist['High'],
                        low=hist['Low'],
                        close=hist['Close'],
                        name='Harga'
                    ))
                    fig.add_trace(go.Scatter(
                        x=hist.index,
                        y=hist['MA20'],
                        name='MA 20',
                        line=dict(color='orange', width=1)
                    ))
                    fig.add_trace(go.Scatter(
                        x=hist.index,
                        y=hist['MA50'],
                        name='MA 50',
                        line=dict(color='green', width=1)
                    ))
                    fig.add_trace(go.Scatter(
                        x=hist.index,
                        y=hist['MA200'],
                        name='MA 200',
                        line=dict(color='purple', width=2)
                    ))
                    fig.update_layout(
                        title=f'Price & Moving Averages - {selected_ticker}',
                        xaxis_rangeslider_visible=False
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with tab_tech2:
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=hist.index,
                        y=hist['RSI14'],
                        name='RSI 14',
                        line=dict(color='blue')
                    ))
                    fig.add_hline(y=70, line_dash="dash", line_color="red")
                    fig.add_hline(y=30, line_dash="dash", line_color="green")
                    fig.update_layout(title='Relative Strength Index (RSI)')
                    
                    fig2 = go.Figure()
                    fig2.add_trace(go.Scatter(
                        x=hist.index,
                        y=hist['MACD'],
                        name='MACD',
                        lin
