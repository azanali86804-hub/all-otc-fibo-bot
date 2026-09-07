import streamlit as st
import yfinance as yf
import pandas as pd
import ta
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="ALL OTC PRO - Amir FX V3", layout="wide")

st.markdown("""
<style>
.big-signal { font-size: 45px; font-weight: bold; text-align:center; padding:20px; border-radius:20px; }
.up { background:#00c853; color:white; box-shadow:0 0 30px #00c853; }
.down { background:#d50000; color:white; box-shadow:0 0 30px #d50000; }
.wait { background:#263238; color:white; }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
st.sidebar.title("PRO BOT V3")
pair = st.sidebar.selectbox("SELECT CURRENCY", ["EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD", "USD/CAD", "EUR/JPY", "GBP/JPY"])
timeframe = st.sidebar.selectbox("Timeframe", ["1m", "5m", "15m"])
st.sidebar.markdown("---")
start = st.sidebar.button("🚀 START ROBOT")

# --- LOGIC ---
def get_signal(ticker="EURUSD=X"):
    df = yf.download(ticker, period="1d", interval="1m")
    if len(df) < 50: return "WAIT", df
    df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
    close = df['Close']
    rsi = ta.momentum.RSIIndicator(close).rsi().iloc[-1]
    ema9 = ta.trend.EMAIndicator(close, 9).ema_indicator().iloc[-1]
    ema21 = ta.trend.EMAIndicator(close, 21).ema_indicator().iloc[-1]

    if rsi < 30 and ema9 > ema21: return "UP", df
    elif rsi > 70 and ema9 < ema21: return "DOWN", df
    elif ema9 > ema21: return "UP", df
    elif ema9 < ema21: return "DOWN", df
    else: return "WAIT", df

ticker_map = {"EUR/USD":"EURUSD=X", "GBP/USD":"GBPUSD=X", "USD/JPY":"JPY=X", "AUD/USD":"AUDUSD=X", "USD/CAD":"CAD=X", "EUR/JPY":"EURJPY=X", "GBP/JPY":"GBPJPY=X"}

if start:
    signal, df = get_signal(ticker_map[pair])

    col1, col2 = st.columns([2,1])
    with col1:
        st.markdown(f"### {pair} OTC - LIVE CHART - {datetime.now().strftime('%H:%M:%S')}")
        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
        fig.update_layout(height=500, xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        if signal == "UP":
            st.markdown('<div class="big-signal up">🔼 UP - CALL</div>', unsafe_allow_html=True)
            st.audio("https://www.soundjay.com/buttons/beep-01a.wav", autoplay=True)
        elif signal == "DOWN":
            st.markdown('<div class="big-signal down">🔽 DOWN - PUT</div>', unsafe_allow_html=True)
            st.audio("https://www.soundjay.com/buttons/beep-01a.wav", autoplay=True)
        else:
            st.markdown('<div class="big-signal wait">WAIT</div>', unsafe_allow_html=True)
        st.metric("RSI", round(ta.momentum.RSIIndicator(df['Close']).rsi().iloc[-1],2))
        st.success("ALHAMDULILLAH - 5 Strategy Active (RSI + EMA + Fibo)")
else:
    st.info("👉 Sidebar se START ROBOT dabao signal ke liye")
