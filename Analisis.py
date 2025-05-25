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

# Fungsi untuk mendapatkan data saham secara aman
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

# Fungsi untuk menghitung indikator teknikal
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

# Fungsi untuk mendapatkan data fundamental secara aman
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

# Fungsi untuk mengevaluasi valuasi
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

# Fungsi untuk proyeksi dividen
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

# Fungsi bunga majemuk
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

# Catatan: UI dan bagian logika utama aplikasi belum disalin ulang untuk efisiensi.
# Silakan lanjutkan logika `st.session_state`, UI tab, dan lainnya menggunakan fungsi-fungsi di atas yang sudah diperbaiki.

st.success("Fungsi backend telah diperbaiki dan siap digunakan. Silakan lanjutkan dengan UI atau saya bantu lengkapi jika diinginkan.")
