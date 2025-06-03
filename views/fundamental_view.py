import streamlit as st
import yfinance as yf
import matplotlib.pyplot as plt
from utils.formatter import format_rupiah
from utils.validator import StockValidator

def show_fundamental_analysis(ticker):
    """Menampilkan analisis fundamental saham"""
    try:
        st.subheader("📊 Analisis Fundamental")
        
        # Ambil data fundamental
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Layout kolom
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**Info Perusahaan**")
            st.write(f"Nama: {info.get('longName', 'N/A')}")
            st.write(f"Sektor: {info.get('sector', 'N/A')}")
            st.write(f"Industri: {info.get('industry', 'N/A')}")
            st.write(f"Negara: {info.get('country', 'N/A')}")
        
        with col2:
            st.markdown("**Valuasi**")
            st.write(f"P/E: {info.get('trailingPE', 'N/A')}")
            st.write(f"P/B: {info.get('priceToBook', 'N/A')}")
            st.write(f"EPS: {format_rupiah(info.get('trailingEps', 0))}")
            st.write(f"Dividen Yield: {info.get('dividendYield', 'N/A')}")
        
        with col3:
            st.markdown("**Kinerja**")
            st.write(f"ROE: {info.get('returnOnEquity', 'N/A')}")
            st.write(f"ROA: {info.get('returnOnAssets', 'N/A')}")
            st.write(f"Profit Margin: {info.get('profitMargins', 'N/A')}")
            st.write(f"Debt/Equity: {info.get('debtToEquity', 'N/A')}")
        
        # Laporan keuangan
        st.markdown("**Laporan Keuangan**")
        tab1, tab2, tab3 = st.tabs(["Income Statement", "Balance Sheet", "Cash Flow"])
        
        with tab1:
            financials = stock.financials
            if not financials.empty:
                fig, ax = plt.subplots(figsize=(10, 4))
                financials.loc[['Total Revenue', 'Net Income']].T.plot(kind='bar', ax=ax)
                st.pyplot(fig)
        
        with tab2:
            balance_sheet = stock.balance_sheet
            if not balance_sheet.empty:
                fig, ax = plt.subplots(figsize=(10, 4))
                balance_sheet.loc[['Total Assets', 'Total Liab', 'Total Stockholder Equity']].T.plot(kind='bar', ax=ax)
                st.pyplot(fig)
        
        with tab3:
            cashflow = stock.cashflow
            if not cashflow.empty:
                fig, ax = plt.subplots(figsize=(10, 4))
                cashflow.loc[['Operating Cashflow', 'Investing Cashflow', 'Financing Cashflow']].T.plot(kind='bar', ax=ax)
                st.pyplot(fig)
    
    except Exception as e:
        st.error(f"Gagal memuat data fundamental: {str(e)}")
