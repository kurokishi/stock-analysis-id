import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
import requests
from bs4 import BeautifulSoup
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(layout="wide", page_title="Portofolio Saham Analyzer")

# === Fungsi Backend ===
def get_stock_data(ticker, period='1y'):
    try:
        stock = yf.Ticker(ticker + ".JK")
        hist = stock.history(period=period)
        if hist.empty:
            raise ValueError("Data historis kosong.")
        return stock, hist
    except Exception as e:
        st.error(f"Gagal mengambil data historis untuk {ticker}: {e}")
        return None, pd.DataFrame()

def calculate_technical_indicators(df):
    df['MA50'] = df['Close'].rolling(window=50).mean()
    df['MA200'] = df['Close'].rolling(window=200).mean()
    delta = df['Close'].diff()
    gain = delta.where(delta > 0, 0).rolling(window=14).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    exp12 = df['Close'].ewm(span=12, adjust=False).mean()
    exp26 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = exp12 - exp26
    df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    return df

def get_fundamental_data(ticker):
    try:
        url = f"https://finance.yahoo.com/quote/{ticker}.JK/key-statistics"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        def extract_value(data_test_id):
            element = soup.find("td", {"data-test": data_test_id})
            if element and element.text != 'N/A':
                return element.text.strip()
            return None

        pe_text = extract_value("PE_RATIO-value")
        pb_text = extract_value("PB_RATIO-value")
        dy_text = extract_value("DIVIDEND_AND_YIELD-value")

        pe = float(pe_text) if pe_text else np.nan
        pb = float(pb_text) if pb_text else np.nan
        dy = float(dy_text.split('(')[1].split('%')[0]) / 100 if dy_text and '(' in dy_text else np.nan

        return {'PER': pe, 'PBV': pb, 'Dividend Yield': dy}
    except Exception as e:
        st.warning(f"Gagal mengambil data fundamental untuk {ticker}: {e}")
        return {'PER': np.nan, 'PBV': np.nan, 'Dividend Yield': np.nan}

def evaluate_valuation(pe, pb, industry_pe=15, industry_pb=2):
    if pd.isna(pe) or pd.isna(pb):
        return "Data tidak tersedia"
    pe_score = 2 if pe < industry_pe * 0.7 else 1 if pe < industry_pe else -1 if pe > industry_pe * 1.3 else 0
    pb_score = 2 if pb < industry_pb * 0.7 else 1 if pb < industry_pb else -1 if pb > industry_pb * 1.3 else 0
    total_score = pe_score + pb_score
    if total_score >= 3:
        return "Undervalued"
    elif total_score >= 1:
        return "Fairly valued"
    else:
        return "Overvalued"

def calculate_dividend_projection(ticker, shares, current_price):
    try:
        stock = yf.Ticker(ticker + ".JK")
        dividends = stock.dividends
        if not dividends.empty:
            avg_dividend = dividends[-4:].mean()
            dividend_per_share = avg_dividend / current_price if current_price else 0
            return shares * dividend_per_share
        else:
            return 0
    except Exception as e:
        st.warning(f"Gagal menghitung dividen untuk {ticker}: {e}")
        return 0

def compound_interest_simulation(initial_value, growth_rate, years, dividend_yield=0, reinvest=True):
    results = []
    current_value = initial_value
    for year in range(1, years+1):
        capital_growth = current_value * (1 + growth_rate)
        dividends = current_value * dividend_yield
        current_value = capital_growth + dividends if reinvest else capital_growth
        results.append({
            'Year': year,
            'Portfolio Value': current_value,
            'Dividends': 0 if reinvest else dividends
        })
    return pd.DataFrame(results)

def get_recommendation(valuation, ma50, ma200, rsi):
    if valuation == "Undervalued" and ma50 > ma200 and rsi < 70:
        return "Beli"
    elif valuation == "Overvalued" and rsi > 70:
        return "Jual"
    else:
        return "Tahan"

# === UI Antarmuka ===
st.title("Asisten Analisis Portofolio Saham")

if 'portfolio' not in st.session_state:
    st.session_state.portfolio = pd.DataFrame(columns=['Ticker', 'Shares', 'Buy Price'])

with st.sidebar:
    st.header("Tambah Saham")
    kode = st.text_input("Kode Saham (tanpa .JK)", value="BBCA").upper()
    lot = st.number_input("Jumlah Lot", value=1, min_value=1)
    harga_beli = st.number_input("Harga Beli per Saham", value=1000, min_value=1)
    if st.button("Tambahkan"):
        saham_baru = {'Ticker': kode, 'Shares': lot * 100, 'Buy Price': harga_beli}
        st.session_state.portfolio = pd.concat([st.session_state.portfolio, pd.DataFrame([saham_baru])], ignore_index=True)
        st.success(f"{kode} berhasil ditambahkan.")

st.subheader("Portofolio Saat Ini")
if st.session_state.portfolio.empty:
    st.info("Belum ada saham ditambahkan.")
else:
    st.dataframe(st.session_state.portfolio)

    total_nilai = 0
    for idx, row in st.session_state.portfolio.iterrows():
        ticker = row['Ticker']
        shares = row['Shares']
        buy_price = row['Buy Price']
        stock, hist = get_stock_data(ticker)
        if hist.empty:
            continue
        current_price = hist['Close'].iloc[-1]
        nilai_saham = shares * current_price
        total_nilai += nilai_saham

        st.markdown(f"### {ticker}")
        st.write(f"Harga Saat Ini: Rp{current_price:,.0f}")
        st.write(f"Nilai: Rp{nilai_saham:,.0f}")

        fundamental = get_fundamental_data(ticker)
        st.write(f"PER: {fundamental['PER']:.2f} | PBV: {fundamental['PBV']:.2f} | Yield: {fundamental['Dividend Yield']:.2%}")
        valuasi = evaluate_valuation(fundamental['PER'], fundamental['PBV'])
        st.write(f"Valuasi: **{valuasi}**")

        hist = calculate_technical_indicators(hist)
        fig = go.Figure()
        fig.add_trace(go.Candlestick(x=hist.index, open=hist['Open'], high=hist['High'], low=hist['Low'], close=hist['Close']))
        fig.add_trace(go.Scatter(x=hist.index, y=hist['MA50'], line=dict(color='blue'), name='MA50'))
        fig.add_trace(go.Scatter(x=hist.index, y=hist['MA200'], line=dict(color='red'), name='MA200'))
        fig.update_layout(title=f"Grafik Harga {ticker}", xaxis_title="Tanggal", yaxis_title="Harga")
        st.plotly_chart(fig, use_container_width=True)

        annual_div = calculate_dividend_projection(ticker, shares, current_price)
        st.write(f"Perkiraan Dividen Tahunan: Rp{annual_div:,.0f}")

        rsi = hist['RSI'].iloc[-1]
        ma50 = hist['MA50'].iloc[-1]
        ma200 = hist['MA200'].iloc[-1]
        rekomendasi = get_recommendation(valuasi, ma50, ma200, rsi)
        st.write(f"**Rekomendasi: {rekomendasi}**")

    st.markdown(f"## Total Nilai Portofolio: Rp{total_nilai:,.0f}")
            
