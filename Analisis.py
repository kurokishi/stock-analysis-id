import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
import requests
from bs4 import BeautifulSoup
import json
import warnings
warnings.filterwarnings('ignore')

# Konfigurasi awal
st.set_page_config(layout="wide", page_title="Portofolio Saham Analyzer")

# Fungsi untuk mendapatkan data saham
def get_stock_data(ticker, period='1y'):
    stock = yf.Ticker(ticker + ".JK")
    hist = stock.history(period=period)
    return stock, hist

# Fungsi untuk menghitung indikator teknikal
def calculate_technical_indicators(df):
    df['MA50'] = df['Close'].rolling(window=50).mean()
    df['MA200'] = df['Close'].rolling(window=200).mean()
    
    # Hitung RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # Hitung MACD
    exp12 = df['Close'].ewm(span=12, adjust=False).mean()
    exp26 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = exp12 - exp26
    df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    
    return df

# Fungsi untuk mendapatkan data fundamental
def get_fundamental_data(ticker):
    try:
        url = f"https://finance.yahoo.com/quote/{ticker}.JK/key-statistics"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Ini adalah contoh sederhana, perlu disesuaikan dengan struktur halaman sebenarnya
        pe_ratio = soup.find("td", {"data-test": "PE_RATIO-value"}).text
        pb_ratio = soup.find("td", {"data-test": "PB_RATIO-value"}).text
        dividend_yield = soup.find("td", {"data-test": "DIVIDEND_AND_YIELD-value"}).text.split('(')[1].split(')')[0]
        
        return {
            'PER': float(pe_ratio),
            'PBV': float(pb_ratio),
            'Dividend Yield': float(dividend_yield.strip('%')) / 100
        }
    except:
        return {
            'PER': np.nan,
            'PBV': np.nan,
            'Dividend Yield': np.nan
        }

# Fungsi untuk mengevaluasi valuasi
def evaluate_valuation(pe, pb, industry_pe=15, industry_pb=2):
    if pd.isna(pe) or pd.isna(pb):
        return "Data tidak tersedia"
    
    pe_score = 0
    pb_score = 0
    
    if pe < industry_pe * 0.7:
        pe_score = 2
    elif pe < industry_pe:
        pe_score = 1
    elif pe > industry_pe * 1.3:
        pe_score = -1
    
    if pb < industry_pb * 0.7:
        pb_score = 2
    elif pb < industry_pb:
        pb_score = 1
    elif pb > industry_pb * 1.3:
        pb_score = -1
    
    total_score = pe_score + pb_score
    
    if total_score >= 3:
        return "Undervalued"
    elif total_score >= 1:
        return "Fairly valued"
    else:
        return "Overvalued"

# Fungsi untuk proyeksi dividen
def calculate_dividend_projection(ticker, shares, current_price):
    try:
        stock = yf.Ticker(ticker + ".JK")
        dividends = stock.dividends
        if len(dividends) > 0:
            avg_dividend = dividends[-4:].mean()  # Rata-rata 4 dividen terakhir
            dividend_per_share = avg_dividend / current_price
            annual_dividend = shares * dividend_per_share
            return annual_dividend
        else:
            return 0
    except:
        return 0

# Fungsi untuk simulasi bunga majemuk
def compound_interest_simulation(initial_value, growth_rate, years, dividend_yield=0, reinvest=True):
    results = []
    current_value = initial_value
    for year in range(1, years+1):
        capital_growth = current_value * (1 + growth_rate)
        dividends = current_value * dividend_yield
        if reinvest:
            current_value = capital_growth + dividends
        else:
            current_value = capital_growth
        results.append({
            'Year': year,
            'Portfolio Value': current_value,
            'Dividends': dividends if not reinvest else 0
        })
    return pd.DataFrame(results)

# Inisialisasi session state untuk portofolio
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = pd.DataFrame(columns=['Ticker', 'Shares', 'Buy Price', 'Current Price', 'Value'])

# UI Aplikasi
st.title("🤑 Asisten Analisis Portofolio Saham")
st.markdown("""
**Aplikasi ini membantu Anda menganalisis dan mengelola portofolio saham pribadi** dengan fitur:
- Analisis fundamental & teknikal
- Rekomendasi alokasi modal baru
- Indikator jual/tahan/tambah
- Simulasi pertumbuhan portofolio
""")

# Tab navigasi
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Portofolio Saat Ini", 
    "Analisis Saham", 
    "Rekomendasi Alokasi", 
    "Indikator Jual/Tahan/Tambah", 
    "Simulasi Pertumbuhan"
])

with tab1:
    st.header("📊 Portofolio Saat Ini")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Tambah/Edit Saham")
        with st.form("portfolio_form"):
            ticker = st.text_input("Kode Saham (contoh: BBCA)", "").upper()
            shares = st.number_input("Jumlah Lot", min_value=1, value=1)
            buy_price = st.number_input("Harga Beli per Saham (Rp)", min_value=1, value=1000)
            
            submitted = st.form_submit_button("Tambahkan ke Portofolio")
            if submitted and ticker:
                try:
                    stock_data = yf.Ticker(ticker + ".JK")
                    current_price = stock_data.history(period='1d')['Close'].iloc[-1]
                    
                    new_row = {
                        'Ticker': ticker,
                        'Shares': shares * 100,  # Convert lot to shares
                        'Buy Price': buy_price,
                        'Current Price': current_price,
                        'Value': shares * 100 * current_price
                    }
                    
                    if ticker in st.session_state.portfolio['Ticker'].values:
                        st.session_state.portfolio.loc[st.session_state.portfolio['Ticker'] == ticker] = pd.Series(new_row)
                    else:
                        st.session_state.portfolio = st.session_state.portfolio.append(new_row, ignore_index=True)
                    
                    st.success(f"{ticker} berhasil ditambahkan/diperbarui!")
                except:
                    st.error("Gagal mendapatkan data saham. Pastikan kode saham benar.")
    
    with col2:
        st.subheader("Hapus Saham")
        if not st.session_state.portfolio.empty:
            to_delete = st.selectbox(
                "Pilih saham untuk dihapus",
                st.session_state.portfolio['Ticker'].unique()
            )
            if st.button("Hapus dari Portofolio"):
                st.session_state.portfolio = st.session_state.portfolio[st.session_state.portfolio['Ticker'] != to_delete]
                st.success(f"{to_delete} berhasil dihapus!")
        else:
            st.info("Portofolio kosong. Tambahkan saham terlebih dahulu.")
    
    st.subheader("Ringkasan Portofolio")
    if not st.session_state.portfolio.empty:
        # Hitung total nilai portofolio
        total_value = st.session_state.portfolio['Value'].sum()
        total_investment = (st.session_state.portfolio['Shares'] * st.session_state.portfolio['Buy Price']).sum()
        profit_loss = total_value - total_investment
        profit_loss_pct = (profit_loss / total_investment) * 100
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Nilai Portofolio", f"Rp{total_value:,.0f}")
        col2.metric("Total Investasi", f"Rp{total_investment:,.0f}")
        col3.metric("Profit/Loss", 
                   f"Rp{profit_loss:,.0f}", 
                   f"{profit_loss_pct:.2f}%",
                   delta_color="inverse" if profit_loss < 0 else "normal")
        
        # Tampilkan tabel portofolio
        st.dataframe(st.session_state.portfolio.style.format({
            'Buy Price': '{:,.0f}',
            'Current Price': '{:,.0f}',
            'Value': '{:,.0f}'
        }), height=300)
        
        # Grafik alokasi portofolio
        fig = px.pie(
            st.session_state.portfolio, 
            names='Ticker', 
            values='Value',
            title='Alokasi Portofolio'
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Portofolio Anda masih kosong. Tambahkan saham untuk memulai analisis.")

with tab2:
    st.header("🔍 Analisis Saham")
    
    if not st.session_state.portfolio.empty:
        selected_ticker = st.selectbox(
            "Pilih saham untuk dianalisis",
            st.session_state.portfolio['Ticker'].unique()
        )
        
        stock_data = st.session_state.portfolio[st.session_state.portfolio['Ticker'] == selected_ticker].iloc[0]
        shares = stock_data['Shares']
        buy_price = stock_data['Buy Price']
        current_price = stock_data['Current Price']
        
        # Dapatkan data historis
        stock, hist = get_stock_data(selected_ticker)
        hist = calculate_technical_indicators(hist)
        
        # Dapatkan data fundamental (simulasi)
        fundamental = get_fundamental_data(selected_ticker)
        valuation_status = evaluate_valuation(fundamental['PER'], fundamental['PBV'])
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Fundamental")
            st.metric("PER", f"{fundamental['PER']:.2f}" if not pd.isna(fundamental['PER']) else "N/A")
            st.metric("PBV", f"{fundamental['PBV']:.2f}" if not pd.isna(fundamental['PBV']) else "N/A")
            st.metric("Dividend Yield", f"{fundamental['Dividend Yield']:.2%}" if not pd.isna(fundamental['Dividend Yield']) else "N/A")
            st.metric("Status Valuasi", valuation_status)
            
            # Analisis AI sederhana (simulasi)
            st.subheader("Analisis AI")
            if valuation_status == "Undervalued":
                st.success("""
                **Potensi Baik**: Saham ini tampak undervalued berdasarkan metrik fundamental. 
                Memiliki ruang untuk apresiasi harga jika kinerja perusahaan tetap baik.
                """)
            elif valuation_status == "Overvalued":
                st.warning("""
                **Hati-hati**: Saham ini tampak overvalued berdasarkan metrik fundamental. 
                Pertimbangkan untuk mengambil profit atau mencari peluang lain.
                """)
            else:
                st.info("""
                **Netral**: Saham ini tampak fairly valued. 
                Pantau perkembangan perusahaan dan kondisi pasar untuk keputusan berikutnya.
                """)
        
        with col2:
            st.subheader("Teknikal")
            # Grafik harga
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
                y=hist['MA50'],
                name='MA 50',
                line=dict(color='orange')
            ))
            fig.add_trace(go.Scatter(
                x=hist.index,
                y=hist['MA200'],
                name='MA 200',
                line=dict(color='purple')
            ))
            fig.update_layout(title=f'Performa Harga {selected_ticker}')
            st.plotly_chart(fig, use_container_width=True)
            
            # Grafik RSI
            fig_rsi = go.Figure()
            fig_rsi.add_trace(go.Scatter(
                x=hist.index,
                y=hist['RSI'],
                name='RSI'
            ))
            fig_rsi.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Overbought")
            fig_rsi.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Oversold")
            fig_rsi.update_layout(title='Indikator RSI (14 hari)')
            st.plotly_chart(fig_rsi, use_container_width=True)
        
        # Proyeksi dividen
        st.subheader("Proyeksi Dividen")
        annual_dividend = calculate_dividend_projection(selected_ticker, shares, current_price)
        st.metric("Estimasi Dividen Tahunan", f"Rp{annual_dividend:,.0f}")
        
    else:
        st.info("Portofolio Anda masih kosong. Tambahkan saham terlebih dahulu untuk melihat analisis.")

with tab3:
    st.header("💰 Rekomendasi Alokasi Modal Baru")
    
    if not st.session_state.portfolio.empty:
        new_capital = st.number_input("Masukkan jumlah modal baru (Rp)", min_value=1000000, value=5000000, step=1000000)
        
        if st.button("Buat Rekomendasi Alokasi"):
            # Sederhananya, kita akan merekomendasikan alokasi berdasarkan valuasi dan dividen
            portfolio = st.session_state.portfolio.copy()
            
            # Hitung skor untuk setiap saham
            portfolio['Valuation Score'] = portfolio.apply(lambda row: 
                3 if evaluate_valuation(get_fundamental_data(row['Ticker'])['PER'], 
                                      get_fundamental_data(row['Ticker'])['PBV']) == "Undervalued" else
                1 if evaluate_valuation(get_fundamental_data(row['Ticker'])['PER'], 
                                      get_fundamental_data(row['Ticker'])['PBV']) == "Fairly valued" else
                0, axis=1)
            
            portfolio['Dividend Score'] = portfolio.apply(lambda row: 
                get_fundamental_data(row['Ticker'])['Dividend Yield'] * 100, axis=1)
            
            # Gabungkan skor (50% valuasi, 50% dividen)
            portfolio['Total Score'] = 0.5 * portfolio['Valuation Score'] + 0.5 * portfolio['Dividend Score']
            portfolio['Allocation %'] = portfolio['Total Score'] / portfolio['Total Score'].sum()
            portfolio['Recommended Allocation'] = (portfolio['Allocation %'] * new_capital).astype(int)
            
            # Tampilkan hasil
            st.subheader("Rekomendasi Alokasi Modal")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.dataframe(portfolio[['Ticker', 'Recommended Allocation']].sort_values(
                    'Recommended Allocation', ascending=False).style.format({
                    'Recommended Allocation': '{:,.0f}'
                }))
            
            with col2:
                fig = px.pie(
                    portfolio, 
                    names='Ticker', 
                    values='Recommended Allocation',
                    title='Alokasi Rekomendasi'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Penjelasan strategi
            st.subheader("Strategi dan Asumsi")
            st.markdown("""
            **Strategi Alokasi**:
            - Prioritas diberikan kepada saham yang:
              * Undervalued berdasarkan PER dan PBV
              * Memiliki dividend yield tinggi
            - Modal dialokasikan secara proporsional berdasarkan skor kombinasi valuasi dan dividen
            
            **Asumsi**:
            - Data fundamental diambil dari sumber publik (simulasi)
            - Rekomendasi ini tidak mempertimbangkan faktor eksternal seperti kondisi pasar atau berita perusahaan
            - Selalu lakukan riset tambahan sebelum mengambil keputusan investasi
            """)
    else:
        st.info("Portofolio Anda masih kosong. Tambahkan saham terlebih dahulu untuk mendapatkan rekomendasi.")

with tab4:
    st.header("📈 Indikator Jual/Tahan/Tambah")
    
    if not st.session_state.portfolio.empty:
        st.markdown("""
        **Rekomendasi untuk setiap saham dalam portofolio Anda** berdasarkan:
        - Valuasi saat ini
        - Tren harga
        - Potensi dividen
        """)
        
        recommendations = []
        for _, row in st.session_state.portfolio.iterrows():
            ticker = row['Ticker']
            shares = row['Shares']
            buy_price = row['Buy Price']
            current_price = row['Current Price']
            
            # Dapatkan data fundamental
            fundamental = get_fundamental_data(ticker)
            valuation_status = evaluate_valuation(fundamental['PER'], fundamental['PBV'])
            
            # Hitung profit/loss
            profit_loss = (current_price - buy_price) * shares
            profit_loss_pct = (current_price - buy_price) / buy_price * 100
            
            # Buat rekomendasi sederhana
            if valuation_status == "Undervalued" and profit_loss_pct < 20:
                action = "Tambah"
                reason = "Undervalued dengan potensi kenaikan"
                risk_reward = "Rendah-Risiko/Tinggi-Reward"
            elif valuation_status == "Overvalued" and profit_loss_pct > 0:
                action = "Jual Sebagian"
                reason = "Overvalued dengan profit positif"
                risk_reward = "Tinggi-Risiko/Rendah-Reward"
            elif profit_loss_pct > 30:
                action = "Jual Sebagian"
                reason = "Profit sudah signifikan"
                risk_reward = "Sedang-Risiko/Sedang-Reward"
            else:
                action = "Tahan"
                reason = "Valuasi wajar dan tren positif"
                risk_reward = "Sedang-Risiko/Sedang-Reward"
            
            recommendations.append({
                'Ticker': ticker,
                'Profit/Loss (Rp)': profit_loss,
                'Profit/Loss (%)': profit_loss_pct,
                'Valuation': valuation_status,
                'Action': action,
                'Reason': reason,
                'Risk/Reward': risk_reward
            })
        
        df_recommendations = pd.DataFrame(recommendations)
        st.dataframe(df_recommendations.style.format({
            'Profit/Loss (Rp)': '{:,.0f}',
            'Profit/Loss (%)': '{:.2f}%'
        }), height=400)
        
        # Grafik rekomendasi
        fig = px.bar(
            df_recommendations,
            x='Ticker',
            y='Profit/Loss (%)',
            color='Action',
            title='Rekomendasi Aksi untuk Portofolio',
            text='Profit/Loss (%)'
        )
        st.plotly_chart(fig, use_container_width=True)
        
    else:
        st.info("Portofolio Anda masih kosong. Tambahkan saham terlebih dahulu untuk melihat rekomendasi.")

with tab5:
    st.header("📊 Simulasi Pertumbuhan Portofolio")
    
    if not st.session_state.portfolio.empty:
        # Hitung rata-rata pertumbuhan historis portofolio
        total_growth = 0
        dividend_yield = 0
        count = 0
        
        for _, row in st.session_state.portfolio.iterrows():
            ticker = row['Ticker']
            try:
                stock = yf.Ticker(ticker + ".JK")
                hist = stock.history(period='5y')
                if len(hist) > 1:
                    start_price = hist['Close'].iloc[0]
                    end_price = hist['Close'].iloc[-1]
                    growth = (end_price - start_price) / start_price / 5  # Pertumbuhan tahunan
                    total_growth += growth
                    
                    # Hitung dividend yield
                    dividends = stock.dividends
                    if len(dividends) > 0:
                        avg_dividend = dividends[-4:].mean()
                        dividend_yield += avg_dividend / end_price
                    
                    count += 1
            except:
                continue
        
        if count > 0:
            avg_growth = total_growth / count
            avg_dividend_yield = dividend_yield / count
        else:
            avg_growth = 0.1  # Default 10% jika tidak ada data
    
