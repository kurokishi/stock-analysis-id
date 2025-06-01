from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from enum import Enum, auto

class ModelType(Enum):
    """Jenis model prediksi yang digunakan"""
    PROPHET = auto()
    ARIMA = auto()
    LSTM = auto()

@dataclass 
class ForecastInterval:
    """Interval kepercayaan prediksi"""
    lower: float
    upper: float
    confidence_level: float = 0.95  # 95% confidence

@dataclass
class PredictionResult:
    """
    Model hasil prediksi harga saham
    """
    ticker: str
    model_type: ModelType
    prediction_dates: List[datetime]
    predicted_values: List[float]
    confidence_intervals: List[ForecastInterval]
    actual_values: Optional[List[float]] = None
    model_metrics: Optional[Dict[str, float]] = None
    
    def get_metrics_summary(self) -> Dict[str, str]:
        """Return formatted metrics summary"""
        if not self.model_metrics:
            return {}
            
        return {
            'MAE': f"{self.model_metrics.get('mae', 0):.2f}",
            'MSE': f"{self.model_metrics.get('mse', 0):.2f}",
            'RMSE': f"{self.model_metrics.get('rmse', 0):.2f}",
            'MAPE': f"{self.model_metrics.get('mape', 0):.2f}%",
            'R-squared': f"{self.model_metrics.get('r2', 0):.4f}"
        }
    
    def to_dataframe(self):
        """Convert prediction to pandas DataFrame"""
        import pandas as pd
        
        data = {
            'Tanggal': self.prediction_dates,
            'Prediksi': self.predicted_values,
            'Bawah': [i.lower for i in self.confidence_intervals],
            'Atas': [i.upper for i in self.confidence_intervals]
        }
        
        if self.actual_values:
            data['Aktual'] = self.actual_values
            
        return pd.DataFrame(data)
