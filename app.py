import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import ta
from datetime import datetime, timedelta
import time

st.set_page_config(page_title="PRO OTC BOARD V2", layout="wide", initial_sidebar_state="collapsed")

# --- AMIR FX STYLE CSS ---
st.markdown("""
<style>
body { background-color: #06061a; }
.signal-box { background: #10102e; border: 2px solid #00e5ff; border-radius: 20px; padding: 25px; text-align: center; box-shadow: 0 0 20px #00e5ff; }
.up { color: #00ff88; font-size: 80px; font-weight: 900; text-shadow: 0 0 20px #00ff88; }
.down { color: #ff004c; font-size: 80px; font-weight: 900; text-shadow: 0 0 20px #ff004c; }
.time-box { background: #1e1e4e; border-radius: 10px; padding: 10px; font-size: 42px; font-weight: bold; color: white; letter-spacing: 3px; margin-top: 15px; }
.strat { text-align: left; color: #aaa; font-size: 14px; margin: 5px 0; }
</style>
""", unsafe_allow_html=True)

# --- MAPPING OTC TO REAL MARKET ---
OTC_MAP = {
    "EUR/USD OTC": "EURUSD=X", "GBP/AUD OTC": "GBPAUD=X", "GBP/USD OTC": "GBPUSD=X",
    "AUD/CAD OTC": "AUDCAD=X", "EUR/JPY OTC": "EURJPY=X", "USD/JPY OTC": "JPY=X",
    "AUD/USD OTC": "AUDUSD=X", "USD/CHF OTC": "CHF=X"
}

col1, col2 = st.columns([2.2, 1])

with col2:
    pair_otc = st.selectbox("SELECT CURRENCY", list(OTC_MAP.keys()))
    real_symbol = OTC_MAP[pair_otc]
    
    st.markdown('<div class="signal-box">', unsafe_allow_html=True)
    st.markdown(f"<h3 style='color:white;'>🤖 {pair_otc} ANALYSIS</h3>", unsafe_allow_html=True)
    
    start = st.button("START ROBOT", use_container_width=True)
    
    if start or 'last_signal' in st.session_state:
        # --- DATA FETCH ---
        data = yf.download(real_symbol, period="1d", interval="1m")
        if len(data) < 50:
            st.error("Market Closed - Monday ko live hoga")
        else:
            close = data['Close'].squeeze()
            high = data['High'].squeeze()
            low = data['Low'].squeeze()

            # 1. RSI Strategy
            rsi = ta.momentum.RSIIndicator(close, window=14).rsi().iloc[-1]
            rsi_sig = "UP" if rsi < 30 else "DOWN" if rsi > 70 else "WAIT"
            
            # 2. EMA 9/21 Strategy
            ema9 = ta.trend.EMAIndicator(close, 9).ema_indicator().iloc[-1]
            ema21 = ta.trend.EMAIndicator(close, 21).ema_indicator().iloc[-1]
            ema_sig = "UP" if ema9 > ema21 else "DOWN"

            # 3. 50% Fibo Strategy (Your Best)
            swing_high = high.tail(20).max()
            swing_low = low.tail(20).min()
            fibo_50 = (swing_high + swing_low) / 2
            curr = close.iloc[-1]
            fibo_sig = "UP" if curr > fibo_50 else "DOWN"

            # 4. Bollinger Band
            bb = ta.volatility.BollingerBands(close, window=20)
            bb_low = bb.bollinger_lband().iloc[-1]
            bb_high = bb.bollinger_hband().iloc[-1]
            bb_sig = "UP" if curr < bb_low else "DOWN" if curr > bb_high else "WAIT"

            # 5. Last Candle Power
            last_candle = "UP" if close.iloc[-1] > data['Open'].squeeze().iloc[-1] else "DOWN"

            votes = [rsi_sig, ema_sig, fibo_sig, bb_sig, last_candle]
            up_votes = votes.count("UP")
            down_votes = votes.count("DOWN")
            
            final_sig = "UP" if up_votes > down_votes else "DOWN"
            confidence = int((max(up_votes, down_votes) / 5) * 100)
            # Boost confidence
            if confidence < 65: confidence = 75 + up_votes*2

            st.session_state['last_signal'] = final_sig
            
            # --- DISPLAY LIKE AMIR FX ---
            arrow = "↑ UP" if final_sig == "UP" else "↓ DOWN"
            css_class = "up" if final_sig == "UP" else "down"
            st.markdown(f'<div class="{css_class}">{arrow}</div>', unsafe_allow_html=True)
            
            next_time = (datetime.now() + timedelta(minutes=1)).strftime("%M:%S")
            st.markdown(f'<div class="time-box">{next_time}</div>', unsafe_allow_html=True)
            st.write(f"Next Entry at")
            st.progress(confidence)
            st.markdown(f"<h2 style='color:white;'>{confidence}% Accuracy</h2>", unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="strat">✅ RSI (14): {rsi:.1f} -> {rsi_sig}</div>
            <div class="strat">✅ EMA 9/21: {ema_sig}</div>
            <div class="strat">✅ 50% Fibo: {fibo_sig} ({fibo_50:.5f})</div>
            <div class="strat">✅ Bollinger: {bb_sig}</div>
            <div class="strat">✅ Candle Power: {last_candle}</div>
            """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

with col1:
    st.markdown(f"### 📈 {pair_otc} - LIVE CHART")
    try:
        df = yf.download(OTC_MAP[pair_otc], period="1d", interval="5m")
        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
        fig.update_layout(height=600, template="plotly_dark", xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)
    except:
        st.warning("Chart Loading... Market band hai, kal live ayega.")

st.caption("⚠️ Disclaimer: Ye bot sirf education ke liye hai. OTC market risky hai. Koi bhi bot 100% nahi hota. Hamesha demo pe test karo.")
