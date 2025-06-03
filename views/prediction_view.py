import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from models.prophet_model import ProphetModel
from models.arima_model import ARIMAModel
from utils.data_fetcher import DataFetcher
from utils.formatter import format_rupiah

def show_prophet_prediction(ticker, days):
    """Menampilkan prediksi menggunakan Prophet"""
    st.subheader("🧙‍♂️ Prediksi dengan Prophet")
    
    # Ambil data
    data = DataFetcher.get_stock_data(ticker)
    if data.empty:
        st.warning("Data tidak tersedia untuk prediksi")
        return
    
    # Pisahkan data train-test
    split_point = int(len(data) * 0.8)
    train = data.iloc[:split_point]
    test = data.iloc[split_point:]
    
    # Latih model
    prophet = ProphetModel()
    prophet.train(train[['Close']])
    
    # Evaluasi
    forecast = prophet.predict(len(test))
    pred_test = forecast.iloc[split_point:]['yhat'].values
    actual_test = test['Close'].values
    metrics = prophet.evaluate(actual_test, pred_test)
    
    # Tampilkan metrik
    st.subheader("📊 Evaluasi Model Prophet")
    cols = st.columns(4)
    cols[0].metric("MAE", f"{metrics['MAE']:.2f}")
    cols[1].metric("MSE", f"{metrics['MSE']:.2f}")
    cols[2].metric("RMSE", f"{metrics['RMSE']:.2f}")
    cols[3].metric("MAPE", f"{metrics['MAPE']:.2f}%")
    
    # Plot evaluasi
    fig_eval = go.Figure()
    fig_eval.add_trace(go.Scatter(
        x=test.index,
        y=actual_test,
        name='Aktual',
        line=dict(color='blue')
    ))
    fig_eval.add_trace(go.Scatter(
        x=test.index,
        y=pred_test,
        name='Prediksi',
        line=dict(color='red', dash='dash')
    ))
    fig_eval.update_layout(
        title="Evaluasi Prediksi (Backtesting)",
        xaxis_title="Tanggal",
        yaxis_title="Harga"
    )
    st.plotly_chart(fig_eval, use_container_width=True)
    
    # Prediksi masa depan
    future_forecast = prophet.predict(days)
    
    # Plot prediksi
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data.index,
        y=data['Close'],
        name='Data Historis',
        line=dict(color='blue')
    ))
    fig.add_trace(go.Scatter(
        x=future_forecast.index,
        y=future_forecast['yhat'],
        name='Prediksi',
        line=dict(color='green', dash='dash')
    ))
    fig.add_trace(go.Scatter(
        x=future_forecast.index.tolist() + future_forecast.index.tolist()[::-1],
        y=future_forecast['yhat_upper'].tolist() + future_forecast['yhat_lower'].tolist()[::-1],
        fill='toself',
        fillcolor='rgba(0,100,80,0.2)',
        line=dict(color='rgba(255,255,255,0)'),
        name="Interval Kepercayaan"
    ))
    fig.update_layout(
        title=f"Prediksi {days} Hari ke Depan",
        xaxis_title="Tanggal",
        yaxis_title="Harga"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Tabel prediksi
    st.subheader("📅 Detail Prediksi")
    pred_df = future_forecast[['yhat', 'yhat_lower', 'yhat_upper']].rename(columns={
        'yhat': 'Prediksi',
        'yhat_lower': 'Batas Bawah',
        'yhat_upper': 'Batas Atas'
    })
    pred_df.index.name = 'Tanggal'
    st.dataframe(pred_df.style.format("{:.2f}"), use_container_width=True)

def show_arima_prediction(ticker, days):
    """Menampilkan prediksi menggunakan ARIMA"""
    st.subheader("📉 Prediksi dengan ARIMA")
    
    # Ambil data
    data = DataFetcher.get_stock_data(ticker)
    if data.empty:
        st.warning("Data tidak tersedia untuk prediksi")
        return
    
    # Pisahkan data train-test
    split_point = int(len(data) * 0.8)
    train = data.iloc[:split_point]
    test = data.iloc[split_point:]
    
    # Latih model
    arima = ARIMAModel()
    arima.train(train[['Close']])
    
    # Evaluasi
    metrics = arima.evaluate(test[['Close']])
    
    # Tampilkan metrik
    st.subheader("📊 Evaluasi Model ARIMA")
    cols = st.columns(4)
    cols[0].metric("MAE", f"{metrics['MAE']:.2f}")
    cols[1].metric("MSE", f"{metrics['MSE']:.2f}")
    cols[2].metric("RMSE", f"{metrics['RMSE']:.2f}")
    cols[3].metric("MAPE", f"{metrics['MAPE']:.2f}%")
    
    # Prediksi masa depan
    predictions = arima.predict(days)
    
    # Plot prediksi
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data.index[-60:],  # Tampilkan 60 hari terakhir
        y=data['Close'].values[-60:],
        name='Data Historis',
        line=dict(color='blue')
    ))
    fig.add_trace(go.Scatter(
        x=predictions.index,
        y=predictions['prediction'],
        name='Prediksi',
        line=dict(color='green', dash='dash')
    ))
    fig.add_trace(go.Scatter(
        x=predictions.index.tolist() + predictions.index.tolist()[::-1],
        y=predictions['lower'].tolist() + predictions['upper'].tolist()[::-1],
        fill='toself',
        fillcolor='rgba(0,100,80,0.2)',
        line=dict(color='rgba(255,255,255,0)'),
        name="Interval Kepercayaan 95%"
    ))
    fig.update_layout(
        title=f"Prediksi {days} Hari ke Depan",
        xaxis_title="Tanggal",
        yaxis_title="Harga"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Analisis sinyal
    last_price = data['Close'].iloc[-1]
    pred_price = predictions['prediction'].iloc[-1]
    change = pred_price - last_price
    change_pct = (change / last_price) * 100
    
    st.subheader("📌 Rekomendasi")
    cols = st.columns(2)
    cols[0].metric(
        "Perubahan Diprediksi",
        format_rupiah(change),
        f"{change_pct:.2f}%"
    )
    
    if change_pct > 2:
        cols[1].success("🟢 BELI - Harga diprediksi naik signifikan")
    elif change_pct < -2:
        cols[1].error("🔴 JUAL - Harga diprediksi turun signifikan")
    else:
        cols[1].info("⚪ TAHAN - Tidak ada sinyal kuat")

def show_price_prediction(ticker):
    """Menampilkan halaman prediksi harga"""
    st.subheader("🔮 Prediksi Harga Saham")
    
    tab1, tab2 = st.tabs(["Prophet", "ARIMA"])
    
    with tab1:
        st.markdown("""
        **Prophet** adalah model forecasting yang dikembangkan oleh Facebook yang cocok untuk data time series 
        dengan pola musiman yang kuat.
        """)
        days = st.slider(
            "Jumlah Hari Prediksi (Prophet):",
            min_value=7,
            max_value=90,
            value=30,
            key="prophet_days"
        )
        if st.button("Jalankan Prediksi Prophet"):
            show_prophet_prediction(ticker, days)
    
    with tab2:
        st.markdown("""
        **ARIMA** (AutoRegressive Integrated Moving Average) adalah model statistik klasik untuk time series
        forecasting yang cocok untuk data stasioner.
        """)
        days = st.slider(
            "Jumlah Hari Prediksi (ARIMA):",
            min_value=1,
            max_value=30,
            value=7,
            key="arima_days"
        )
        if st.button("Jalankan Prediksi ARIMA"):
            show_arima_prediction(ticker, days)
