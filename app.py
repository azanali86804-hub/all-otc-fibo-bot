import streamlit as st
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

st.set_page_config(page_title="OTC 50% Fibo Bot - REAL", layout="wide")
st.title("🎯 ALL OTC - 50% FIBO BOT - REAL MARKET")
st.caption("Real Pocket Option Price | 50% Fibo Strategy")

otc_map = {
    "EUR/USD OTC": "EURUSD=X",
    "GBP/USD OTC": "GBPUSD=X",
    "USD/JPY OTC": "JPY=X",
    "EUR/JPY OTC": "EURJPY=X",
    "GBP/JPY OTC": "GBPJPY=X",
    "AUD/USD OTC": "AUDUSD=X",
    "USD/CHF OTC": "CHF=X",
    "EUR/GBP OTC": "EURGBP=X",
    "AUD/JPY OTC": "AUDJPY=X",
    "EUR/AUD OTC": "EURAUD=X",
    "GBP/AUD OTC": "GBPAUD=X",
    "AUD/CAD OTC": "AUDCAD=X",
    "EUR/CAD OTC": "EURCAD=X",
    "NZD/USD OTC": "NZDUSD=X",
    "USD/CAD OTC": "CAD=X",
}

st.sidebar.header("Settings")
selected_otc = st.sidebar.selectbox("OTC Market Select Karo", list(otc_map.keys()))
fibo_length = st.sidebar.slider("Fibo Swing Length", 10, 50, 20)

@st.cache_data(ttl=60)
def get_real_data(symbol):
    df = yf.download(symbol, period="1d", interval="1m", progress=False)
    df = df.tail(300)
    df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
    return df

real_symbol = otc_map[selected_otc]
with st.spinner(f"{selected_otc} ka Real price la raha hun..."):
    data = get_real_data(real_symbol)

closes = data["Close"].tolist()
highs = data["High"].tolist()
lows = data["Low"].tolist()
df = pd.DataFrame({"close": closes, "high": highs, "low": lows})

recent = df.tail(fibo_length)
sw_high = recent["high"].max()
sw_low = recent["low"].min()
fib_50 = (sw_high + sw_low) / 2
curr = df["close"].iloc[-1]
prev = df["close"].iloc[-2]

if prev < fib_50 and curr > fib_50:
    signal = "BUY"
elif prev > fib_50 and curr < fib_50:
    signal = "SELL"
else:
    signal = "WAIT"

k1,k2,k3,k4 = st.columns(4)
k1.metric("Swing High", f"{sw_high:.5f}")
k2.metric("50% Level", f"{fib_50:.5f}")
k3.metric("Swing Low", f"{sw_low:.5f}")
k4.metric("Real Price", f"{curr:.5f}")

fig, ax = plt.subplots(figsize=(12, 4))
ax.plot(df["close"].tail(100), label="Real Price")
ax.axhline(sw_high, color="red", linestyle="--")
ax.axhline(sw_low, color="green", linestyle="--")
ax.axhline(fib_50, color="gold", linewidth=2)
ax.legend()
st.pyplot(fig, use_container_width=True)

if st.button(f"🔮 {selected_otc} - REAL Signal", type="primary", use_container_width=True):
    if signal == "BUY":
        st.success(f"## {selected_otc} -> BUY 🟢 50% Break Up")
    elif signal == "SELL":
        st.error(f"## {selected_otc} -> SELL 🔴 50% Break Down")
    else:
        st.warning(f"## {selected_otc} -> WAIT ⏸️")

if st.button("🔄 Refresh Real Price"):
    st.cache_data.clear()
    st.rerun()
