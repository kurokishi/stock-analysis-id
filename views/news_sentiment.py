import streamlit as st
import numpy as np
from textblob import TextBlob
import yfinance as yf
from utils.formatter import format_rupiah

def get_news_sentiment(ticker):
    """Menampilkan analisis sentimen berita"""
    try:
        st.subheader("📰 Analisis Sentimen Berita")
        
        # Dapatkan info perusahaan
        stock = yf.Ticker(ticker)
        company_name = stock.info.get('shortName', ticker.split('.')[0])
        current_price = stock.info.get('currentPrice', 0)
        
        # Header dengan info singkat
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**{company_name}** ({ticker})")
        with col2:
            st.metric("Harga Terkini", format_rupiah(current_price))
        
        # Simulasi data berita (dalam implementasi nyata, gunakan API berita)
        example_news = [
            f"{company_name} melaporkan peningkatan pendapatan kuartalan sebesar 15%",
            f"Analis dari Mandiri Sekuritas merekomendasikan beli saham {company_name} dengan target harga Rp{current_price * 1.15:,.0f}",
            f"{company_name} menghadapi tuntutan hukum terkait pelanggaran regulasi",
            f"{company_name} mengumumkan dividen sebesar Rp500 per saham",
            f"CEO {company_name} mengundurkan diri efektif bulan depan",
            f"{company_name} merilis produk baru yang revolusioner di pasar"
        ]
        
        # Analisis sentimen
        sentiments = []
        st.markdown("**Berita Terkini**")
        
        for news in example_news:
            blob = TextBlob(news)
            sentiment = blob.sentiment.polarity
            sentiments.append(sentiment)
            
            # Tampilkan berita dengan warna sesuai sentimen
            col1, col2 = st.columns([4, 1])
            with col1:
                if sentiment > 0.3:
                    st.success(f"📰 {news}")
                elif sentiment < -0.3:
                    st.error(f"📰 {news}")
                else:
                    st.info(f"📰 {news}")
            with col2:
                st.write(f"Sentimen: {sentiment:.2f}")
        
        # Hitung rata-rata sentimen
        if sentiments:
            avg_sentiment = np.mean(sentiments)
            sentiment_label = (
                "Positif" if avg_sentiment > 0.2 
                else "Negatif" if avg_sentiment < -0.2 
                else "Netral"
            )
            
            # Tampilkan metrik sentimen
            st.subheader("📊 Sentimen Keseluruhan")
            col1, col2 = st.columns(2)
            with col1:
                st.metric(
                    "Skor Sentimen Rata-rata", 
                    f"{avg_sentiment:.2f}",
                    sentiment_label
                )
            
            with col2:
                # Visualisasi meter sentimen
                fig = go.Figure(go.Indicator(
                    mode = "gauge+number",
                    value = avg_sentiment,
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    gauge = {
                        'axis': {'range': [-1, 1]},
                        'steps': [
                            {'range': [-1, -0.2], 'color': "red"},
                            {'range': [-0.2, 0.2], 'color': "lightgray"},
                            {'range': [0.2, 1], 'color': "green"}],
                        'threshold': {
                            'line': {'color': "black", 'width': 4},
                            'thickness': 0.75,
                            'value': avg_sentiment}
                    }
                ))
                fig.update_layout(height=200, margin=dict(t=0, b=0))
                st.plotly_chart(fig, use_container_width=True)
            
            # Rekomendasi berdasarkan sentimen
            st.subheader("💡 Rekomendasi")
            if avg_sentiment > 0.3:
                st.success("""
                **Sinyal Kuat BELI**  
                Sentimen berita sangat positif, menunjukkan optimisme pasar terhadap perusahaan.
                """)
            elif avg_sentiment > 0.1:
                st.info("""
                **Sinyal BELI**  
                Sentimen berita cenderung positif, namun perlu konfirmasi dengan analisis teknikal.
                """)
            elif avg_sentiment < -0.3:
                st.error("""
                **Sinyal Kuat JUAL**  
                Sentimen berita sangat negatif, menunjukkan pesimisme pasar terhadap perusahaan.
                """)
            elif avg_sentiment < -0.1:
                st.warning("""
                **Sinyal JUAL**  
                Sentimen berita cenderung negatif, pertimbangkan untuk mengurangi eksposur.
                """)
            else:
                st.info("""
                **Sinyal TAHAN**  
                Sentimen berita netral, tidak ada sinyal kuat untuk membeli atau menjual.
                """)
    
    except Exception as e:
        st.warning(f"Tidak dapat memuat analisis sentimen: {str(e)}")
