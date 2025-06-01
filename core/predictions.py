import numpy as np
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from prophet import Prophet
from typing import Tuple, Dict
from models.prediction import PredictionResult, ForecastInterval, ModelType
from models.stock import StockData

class PredictionModels:
    @staticmethod
    def prophet_predict(stock_data: StockData, periods: int) -> PredictionResult:
        """Prediksi menggunakan Facebook Prophet"""
        df = pd.DataFrame({
            'ds': stock_data.dates,
            'y': stock_data.closes
        })
        
        model = Prophet(daily_seasonality=True)
        model.fit(df)
        
        future = model.make_future_dataframe(periods=periods)
        forecast = model.predict(future)
        
        # Evaluasi model
        train_size = int(len(df) * 0.8)
        actuals = stock_data.closes[train_size:]
        preds = forecast['yhat'].iloc[train_size:len(df)].values
        
        return PredictionResult(
            ticker=stock_data.ticker,
            model_type=ModelType.PROPHET,
            prediction_dates=forecast['ds'].iloc[-periods:].dt.to_pydatetime().tolist(),
            predicted_values=forecast['yhat'].iloc[-periods:].tolist(),
            confidence_intervals=[
                ForecastInterval(
                    lower=row['yhat_lower'],
                    upper=row['yhat_upper']
                ) for _, row in forecast.iloc[-periods:].iterrows()
            ],
            actual_values=actuals[-periods:] if len(actuals) >= periods else None,
            model_metrics=PredictionModels._calculate_metrics(actuals, preds)
        )

    @staticmethod
    def arima_predict(stock_data: StockData, periods: int) -> PredictionResult:
        """Prediksi menggunakan ARIMA"""
        df = pd.DataFrame({
            'date': stock_data.dates,
            'close': stock_data.closes
        }).set_index('date')
        
        # Cari parameter ARIMA terbaik
        best_order = PredictionModels._find_best_arima_order(df['close'])
        
        # Latih model dengan seluruh data
        model = ARIMA(df['close'], order=best_order)
        model_fit = model.fit()
        
        # Buat prediksi
        forecast = model_fit.get_forecast(steps=periods)
        pred_mean = forecast.predicted_mean
        conf_int = forecast.conf_int()
        
        # Generate prediction dates
        last_date = df.index[-1]
        pred_dates = pd.date_range(
            start=last_date + pd.Timedelta(days=1),
            periods=periods
        ).to_pydatetime().tolist()
        
        return PredictionResult(
            ticker=stock_data.ticker,
            model_type=ModelType.ARIMA,
            prediction_dates=pred_dates,
            predicted_values=pred_mean.tolist(),
            confidence_intervals=[
                ForecastInterval(lower=row[0], upper=row[1])
                for row in conf_int.values
            ],
            model_metrics=None  # Diisi saat evaluasi
        )

    @staticmethod
    def _find_best_arima_order(series: pd.Series) -> Tuple[int, int, int]:
        """Temukan parameter ARIMA terbaik menggunakan AIC"""
        best_aic = float('inf')
        best_order = (1, 0, 1)  # Default
        
        for p in range(0, 3):
            for d in range(0, 2):
                for q in range(0, 3):
                    try:
                        model = ARIMA(series, order=(p, d, q))
                        results = model.fit()
                        if results.aic < best_aic:
                            best_aic = results.aic
                            best_order = (p, d, q)
                    except:
                        continue
        return best_order

    @staticmethod
    def _calculate_metrics(actuals: list, preds: list) -> Dict[str, float]:
        """Hitung metrik evaluasi model"""
        if not actuals or not preds or len(actuals) != len(preds):
            return {}
            
        actuals = np.array(actuals)
        preds = np.array(preds)
        
        mae = np.mean(np.abs(preds - actuals))
        mse = np.mean((preds - actuals)**2)
        rmse = np.sqrt(mse)
        mape = np.mean(np.abs((actuals - preds) / actuals)) * 100
        
        return {
            'mae': mae,
            'mse': mse,
            'rmse': rmse,
            'mape': mape
        }
