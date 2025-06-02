import streamlit as st

class PredictionView:
    def __init__(self, data_provider):
        self.data_provider = data_provider
    
    def show(self, ticker):
        st.subheader("Prediksi Saham")
        # Implementasi tampilan prediksi di sini
        st.write("Fitur prediksi akan diimplementasikan di sini")
