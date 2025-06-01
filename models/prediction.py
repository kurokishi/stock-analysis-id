from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Dict
from enum import Enum, auto

class ModelType(Enum):
    """Jenis model prediksi yang didukung"""
    PROPHET = auto()
    ARIMA = auto()
    LSTM = auto()
    
    def __str__(self):
        return self.name.capitalize()

@dataclass
class ForecastInterval:
    """Interval kepercayaan prediksi"""
    lower: float
    upper: float
    confidence_level: float = 0.95
    
    def width(self) -> float:
        """Lebar interval"""
        return self.upper - self.lower

@dataclass
class PredictionResult:
    """Hasil lengkap dari prediksi model"""
    ticker: str
    model_type: ModelType
    prediction_dates: List[datetime]
    predicted_values: List[float]
    confidence_intervals: List[ForecastInterval]
    actual_values: Optional[List[float]] = None
    model_metrics: Optional[Dict[str, float]] = None
    
    def get_price_change(self) -> Optional[float]:
        """Hitung perubahan harga prediksi"""
        if len(self.predicted_values) < 2:
            return None
        return self.predicted_values[-1] - self.predicted_values[0]
    
    def get_metrics_table(self) -> Dict[str, str]:
        """Format metrik untuk ditampilkan di UI"""
        if not self.model_metrics:
            return {}
            
        return {
            'MAE': f"{self.model_metrics.get('mae', 0):.2f}",
            'MSE': f"{self.model_metrics.get('mse', 0):.2f}",
            'RMSE': f"{self.model_metrics.get('rmse', 0):.2f}",
            'MAPE': f"{self.model_metrics.get('mape', 0):.2f}%"
        }
    
    def to_dataframe(self) -> 'pd.DataFrame':
        """Konversi ke Pandas DataFrame"""
        import pandas as pd
        
        data = {
            'date': self.prediction_dates,
            'predicted': self.predicted_values,
            'lower_bound': [x.lower for x in self.confidence_intervals],
            'upper_bound': [x.upper for x in self.confidence_intervals]
        }
        
        if self.actual_values and len(self.actual_values) == len(self.prediction_dates):
            data['actual'] = self.actual_values
            
        return pd.DataFrame(data).set_index('date')
