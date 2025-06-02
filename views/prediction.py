import streamlit as st
from core.prediction import PredictionModels
from models.stock import StockData
from typing import List

class PredictionView:
    def __init__(self, data_provider):
        self.data_provider = data_provider
    
    def show(self, ticker):
        st.subheader(f"Prediksi Harga Saham {ticker}")
        
        # Dapatkan data historis
        stock_data = self._get_stock_data(ticker)
        if stock_data is None:
            st.error("Gagal memuat data saham")
            return
        
        # Pilihan model
        model_type = st.selectbox(
            "Pilih Model Prediksi",
            ["Prophet", "ARIMA"]
        )
        
        # Periode prediksi
        periods = st.slider(
            "Jumlah Hari Prediksi", 
            min_value=1, 
            max_value=365, 
            value=30
        )
        
        if st.button("Buat Prediksi"):
            with st.spinner("Melakukan prediksi..."):
                try:
                    if model_type == "Prophet":
                        result = PredictionModels.prophet_predict(stock_data, periods)
                    else:
                        result = PredictionModels.arima_predict(stock_data, periods)
                    
                    self._display_results(result)
                except Exception as e:
                    st.error(f"Error dalam prediksi: {str(e)}")

    def _get_stock_data(self, ticker) -> StockData:
        """Dapatkan data saham dalam format StockData"""
        try:
            df = self.data_provider.get_historical_data(ticker)
            return StockData(
                ticker=ticker,
                dates=df.index.to_pydatetime().tolist(),
                closes=df['Close'].tolist()
            )
        except Exception as e:
            st.error(f"Error mendapatkan data: {str(e)}")
            return None

    def _display_results(self, result):
        """Tampilkan hasil prediksi"""
        st.subheader("Hasil Prediksi")
        
        # Tampilkan grafik prediksi
        pred_df = pd.DataFrame({
            'Date': result.prediction_dates,
            'Predicted': result.predicted_values,
            'Lower': [x.lower for x in result.confidence_intervals],
            'Upper': [x.upper for x in result.confidence_intervals]
        }).set_index('Date')
        
        st.line_chart(pred_df[['Predicted', 'Lower', 'Upper']])
        
        # Tampilkan metrik evaluasi jika ada
        if result.model_metrics:
            st.subheader("Evaluasi Model")
            cols = st.columns(4)
            cols[0].metric("MAE", f"{result.model_metrics['mae']:.2f}")
            cols[1].metric("MSE", f"{result.model_metrics['mse']:.2f}")
            cols[2].metric("RMSE", f"{result.model_metrics['rmse']:.2f}")
            cols[3].metric("MAPE", f"{result.model_metrics['mape']:.2f}%")
