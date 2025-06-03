import pandas as pd
import numpy as np
from prophet import Prophet

class ProphetModel:
    def __init__(self):
        self.model = None

    def train(self, data):
        """Melatih model Prophet"""
        df = data[['Close']].reset_index()
        df.columns = ['ds', 'y']
        df['ds'] = pd.to_datetime(df['ds']).dt.tz_localize(None)
        
        self.model = Prophet(daily_seasonality=True)
        self.model.fit(df)
        return self.model

    def predict(self, periods):
        """Membuat prediksi"""
        if not self.model:
            raise ValueError("Model belum dilatih")
            
        future = self.model.make_future_dataframe(periods=periods)
        forecast = self.model.predict(future)
        return forecast

    def evaluate(self, actual, predicted):
        """Evaluasi performa model"""
        metrics = {
            'MAE': np.mean(np.abs(predicted - actual)),
            'MSE': np.mean((predicted - actual)**2),
            'RMSE': np.sqrt(np.mean((predicted - actual)**2)),
            'MAPE': np.mean(np.abs((actual - predicted) / actual)) * 100
        }
        return metrics
