class AppConfig:
    def __init__(self):
        self.app_title = "Analisis Saham Lengkap + AI Prediksi"
        self.cache_dir = "cache"
        self.cache_ttl = 1  # in hours
        self.default_tickers = ["UNVR.JK", "BBCA.JK", "TLKM.JK"]
        self.max_prediction_days = 90
