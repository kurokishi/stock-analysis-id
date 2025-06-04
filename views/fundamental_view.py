import streamlit as st
import yfinance as yf
import matplotlib.pyplot as plt
from utils.formatter import format_rupiah
from utils.validator import StockValidator
from utils.data_fetcher import DataFetcher  # Pastikan diimpor

def show_fundamental_analysis(ticker):
    try:
        # Ambil data sekaligus dari yfinance
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Layout kolom
        col1, col2, col3 = st.columns(3)
        
        # Info Perusahaan
        with col1:
            st.markdown("**Info Perusahaan**")
            st.write(f"Nama: {info.get('longName', 'N/A')}")
            st.write(f"Sektor: {info.get('sector', 'N/A')}")
            st.write(f"Industri: {info.get('industry', 'N/A')}")
            st.write(f"Negara: {info.get('country', 'N/A')}")
        
        # Valuasi
        with col2:
            st.markdown("**Valuasi**")
            st.write(f"P/E: {info.get('trailingPE', 'N/A')}")
            st.write(f"P/B: {info.get('priceToBook', 'N/A')}")
            st.write(f"EPS: {format_rupiah(info.get('trailingEps', 0))}")
            st.write(f"Dividen Yield: {info.get('dividendYield', 'N/A')}")
        
        # Kinerja
        with col3:
            st.markdown("**Kinerja**")
            st.write(f"ROE: {info.get('returnOnEquity', 'N/A')}")
            st.write(f"ROA: {info.get('returnOnAssets', 'N/A')}")
            st.write(f"Profit Margin: {info.get('profitMargins', 'N/A')}")
            st.write(f"Debt/Equity: {info.get('debtToEquity', 'N/A')}")
        
        # Laporan keuangan dengan pengecekan kolom
        st.markdown("**Laporan Keuangan**")
        tab1, tab2, tab3 = st.tabs(["Income Statement", "Balance Sheet", "Cash Flow"])
        
        with tab1:
            financials = stock.financials
            if not financials.empty:
                available_cols = [col for col in ['Total Revenue', 'Net Income'] if col in financials.index]
                if available_cols:
                    fig, ax = plt.subplots(figsize=(10, 4))
                    financials.loc[available_cols].T.plot(kind='bar', ax=ax)
                    st.pyplot(fig)
                else:
                    st.warning("Kolom income statement tidak tersedia")
        
        with tab2:
            balance_sheet = stock.balance_sheet
            if not balance_sheet.empty:
                available_cols = [col for col in ['Total Assets', 'Total Liab', 'Total Stockholder Equity'] 
                                if col in balance_sheet.index]
                if available_cols:
                    fig, ax = plt.subplots(figsize=(10, 4))
                    balance_sheet.loc[available_cols].T.plot(kind='bar', ax=ax)
                    st.pyplot(fig)
                else:
                    st.warning("Kolom balance sheet tidak tersedia")
                    st.info(f"Kolom yang ada: {balance_sheet.index.tolist()}")
        
        with tab3:
            cashflow = stock.cashflow
            if not cashflow.empty:
                available_cols = [col for col in ['Operating Cashflow', 'Investing Cashflow', 'Financing Cashflow'] 
                                if col in cashflow.index]
                if available_cols:
                    fig, ax = plt.subplots(figsize=(10, 4))
                    cashflow.loc[available_cols].T.plot(kind='bar', ax=ax)
                    st.pyplot(fig)
                else:
                    st.warning("Kolom cash flow tidak tersedia")
    
    except Exception as e:
        st.error(f"Gagal memuat data fundamental: {str(e)}")
