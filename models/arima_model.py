import numpy as np
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from typing import Tuple, Dict
from utils.validator import StockValidator

class ARIMAModel:
    def __init__(self):
        self.best_order = None
        self.model = None
        self.last_training_date = None

    def find_best_arima(self, data: pd.DataFrame) -> Tuple[tuple, float]:
        """
        Mencari parameter ARIMA terbaik menggunakan AIC
        
        Args:
            data: DataFrame dengan kolom 'Close'
            
        Returns:
            Tuple: (best_order, best_aic)
        """
        best_aic = float("inf")
        best_order = None
        
        # Grid search sederhana
        for p in range(0, 3):  # AR order
            for d in range(0, 2):  # Differencing
                for q in range(0, 3):  # MA order
                    try:
                        model = ARIMA(data, order=(p,d,q))
                        results = model.fit()
                        if results.aic < best_aic:
                            best_aic = results.aic
                            best_order = (p,d,q)
                    except:
                        continue
        
        self.best_order = best_order
        return best_order, best_aic

    def train(self, data: pd.DataFrame) -> None:
        """
        Melatih model ARIMA dengan parameter terbaik
        
        Args:
            data: DataFrame dengan kolom 'Close'
        """
        # Validasi data
        is_valid, msg = StockValidator.validate_dataframe_for_analysis(data)
        if not is_valid:
            raise ValueError(msg)
            
        # Cari parameter terbaik jika belum ada
        if self.best_order is None:
            self.find_best_arima(data)
            
        # Latih model
        self.model = ARIMA(data, order=self.best_order).fit()
        self.last_training_date = data.index[-1]

    def evaluate(self, test_data: pd.DataFrame) -> Dict[str, float]:
        """
        Evaluasi model pada data testing
        
        Args:
            test_data: DataFrame dengan kolom 'Close' untuk testing
            
        Returns:
            Dict: Dictionary berisi metrik evaluasi
        """
        if self.model is None:
            raise ValueError("Model belum dilatih")
            
        history = list(self.model.data.endog)  # Data training
        predictions = []
        
        for t in range(len(test_data)):
            model = ARIMA(history, order=self.best_order)
            model_fit = model.fit()
            output = model_fit.forecast()
            yhat = output[0]
            predictions.append(yhat)
            obs = test_data['Close'].iloc[t]
            history.append(obs)
        
        # Hitung metrik evaluasi
        actual = test_data['Close'].values
        metrics = {
            'MAE': np.mean(np.abs(predictions - actual)),
            'MSE': np.mean((predictions - actual)**2),
            'RMSE': np.sqrt(np.mean((predictions - actual)**2)),
            'MAPE': np.mean(np.abs((actual - predictions) / actual)) * 100
        }
        return metrics

    def predict(self, steps: int = 30, return_ci: bool = True) -> pd.DataFrame:
        """
        Membuat prediksi ke depan
        
        Args:
            steps: Jumlah hari prediksi
            return_ci: Flag untuk mengembalikan confidence interval
            
        Returns:
            DataFrame: Hasil prediksi dengan kolom ['prediction', 'lower', 'upper']
        """
        if self.model is None:
            raise ValueError("Model belum dilatih")
            
        forecast = self.model.get_forecast(steps=steps)
        pred_mean = forecast.predicted_mean
        pred_dates = pd.date_range(
            start=self.last_training_date + pd.Timedelta(days=1),
            periods=steps
        )
        
        result = pd.DataFrame({
            'date': pred_dates,
            'prediction': pred_mean
        }).set_index('date')
        
        if return_ci:
            conf_int = forecast.conf_int()
            result['lower'] = conf_int.iloc[:, 0]
            result['upper'] = conf_int.iloc[:, 1]
            
        return result

    def get_model_summary(self) -> str:
        """Mendapatkan summary model dalam format text"""
        if self.model is None:
            return "Model belum dilatih"
        return str(self.model.summary())
