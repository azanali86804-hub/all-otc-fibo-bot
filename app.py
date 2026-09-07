import streamlit as st
import yfinance as yf
import pandas as pd
import ta
from datetime import datetime
import time

st.set_page_config(page_title="AMIR FX - FINAL PRO", layout="wide")

# --- STYLISH CSS (Amir FX jaisa) ---
st.markdown("""
<style>
.stApp { background: #0e1117; }
.card { padding:18px; border-radius:15px; text-align:center; font-weight:bold; color:white; margin:5px; box-shadow: 0 4px 20px rgba(0,0,0,0.5); border:1px solid #2a2e39; }
.up { background: linear-gradient(135deg, #00c853, #009624); animation: pulse 1.5s infinite; }
.down { background: linear-gradient(135deg, #d50000, #9b0000); animation: pulse 1.5s infinite; }
.wait { background: #263238; }
@keyframes pulse { 0%{transform:scale(1)} 50%{transform:scale(1.05)} 100%{transform:scale(1)} }
.title { font-size:32px; font-weight:900; color:white; text-align:center; letter-spacing:2px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">💎 AMIR FX - ALL OTC PRO BOARD - LIVE 💎</div>', unsafe_allow_html=True)
st.markdown(f"<p style='text-align:center; color:#00e676;'>ALHAMDULILLAH | LIVE TIME: {datetime.now().strftime('%H:%M:%S')} | 5 STRATEGY ACTIVE</p>", unsafe_allow_html=True)

# --- ALL PAIRS ---
pairs = {
 "EUR/USD OTC": "EURUSD=X", "GBP/USD OTC": "GBPUSD=X", "USD/JPY OTC": "JPY=X",
 "AUD/USD OTC": "AUDUSD=X", "EUR/JPY OTC": "EURJPY=X", "GBP/JPY OTC": "GBPJPY=X",
 "USD/CAD OTC": "CAD=X", "AUD/CAD OTC": "AUDCAD=X", "EUR/GBP OTC": "EURGBP=X",
 "USD/CHF OTC": "CHF=X", "NZD/USD OTC": "NZDUSD=X", "EUR/AUD OTC": "EURAUD=X"
}

def get_signal(ticker):
    try:
        df = yf.download(ticker, period="1d", interval="1m", progress=False)
        if len(df) < 30: return "WAIT", 50
        df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
        close = df['Close']
        rsi = float(ta.momentum.RSIIndicator(close).rsi().iloc[-1])
        ema9 = float(ta.trend.EMAIndicator(close, 9).ema_indicator().iloc[-1])
        ema21 = float(ta.trend.EMAIndicator(close, 21).ema_indicator().iloc[-1])
        # Fibo Logic
        high = float(df['High'].tail(20).max())
        low = float(df['Low'].tail(20).min())
        last = float(close.iloc[-1])
        fibo_up = low + (high-low)*0.618

        if last > fibo_up and ema9 > ema21 and rsi < 65: return "UP", rsi
        elif last < fibo_up and ema9 < ema21 and rsi > 35: return "DOWN", rsi
        elif ema9 > ema21: return "UP", rsi
        else: return "DOWN", rsi
    except: return "WAIT", 50

# --- BOARD ---
cols = st.columns(4)
i=0
for name, ticker in pairs.items():
    sig, rsi = get_signal(ticker)
    css_class = "up" if sig=="UP" else "down" if sig=="DOWN" else "wait"
    arrow = "🔼 CALL" if sig=="UP" else "🔽 PUT" if sig=="DOWN" else "WAIT"
    with cols[i%4]:
        st.markdown(f"<div class='card {css_class}'><div style='font-size:14px'>{name}</div><div style='font-size:20px; margin:8px 0'>{arrow}</div><div style='font-size:12px'>RSI: {round(rsi,1)}</div></div>", unsafe_allow_html=True)
    i+=1

st.markdown("---")
c1, c2 = st.columns([1,3])
with c1:
    if st.button("🔄 REFRESH NOW", use_container_width=True):
        st.rerun()
    st.success("Beep Sound: ON")
    # SOUND
    st.audio("https://www.soundjay.com/buttons/beep-07a.wav", autoplay=True)

with c2:
    st.info("💡 Signal har 30 second me auto change hota hai. Pocket Option / Quotex me 1 MIN trade lo. ALHAMDULILLAH!")

# Auto Refresh
time.sleep(30)
st.rerun()
