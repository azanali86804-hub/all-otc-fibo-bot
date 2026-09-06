import streamlit as st
import pandas as pd
import random
import matplotlib.pyplot as plt

st.set_page_config(page_title="OTC 50% Fibo Bot", layout="wide")
st.title("🎯 ALL OTC - 50% FIBO BOT")
st.caption("Sirf Tumhari 50% Fibo Strategy | No Extra Indicators")

all_otc = [
    "EUR/USD OTC", "GBP/USD OTC", "USD/JPY OTC", "EUR/JPY OTC",
    "GBP/JPY OTC", "AUD/USD OTC", "USD/CHF OTC", "EUR/GBP OTC",
    "AUD/JPY OTC", "EUR/AUD OTC", "GBP/AUD OTC", "AUD/CAD OTC",
    "AUD/CHF OTC", "CAD/JPY OTC", "CHF/JPY OTC", "EUR/CAD OTC",
    "GBP/CAD OTC", "EUR/CHF OTC", "NZD/USD OTC", "USD/CAD OTC"
]

st.sidebar.header("Settings")
selected_market = st.sidebar.selectbox("OTC Market Select Karo", all_otc)
fibo_length = st.sidebar.slider("Fibo Swing Length", 10, 50, 20)

random.seed(hash(selected_market) % 7777)
price = 100
closes, highs, lows = [], [], []
for i in range(300):
    move = random.choice([-1.8, -0.8, 0.8, 1.8])
    price += move
    close = price + random.uniform(-0.3, 0.3)
    high = close + random.uniform(0.2, 1.0)
    low = close - random.uniform(0.2, 1.0)
    closes.append(round(close, 3))
    highs.append(round(high, 3))
    lows.append(round(low, 3))

df = pd.DataFrame({"close": closes, "high": highs, "low": lows})

def get_fibo_signal(df, length):
    recent = df.tail(length)
    swing_high = recent["high"].max()
    swing_low = recent["low"].min()
    fibo_50 = (swing_high + swing_low) / 2
    current_price = df["close"].iloc[-1]
    prev_price = df["close"].iloc[-2]
    if prev_price < fibo_50 and current_price > fibo_50:
        return "BUY", swing_high, swing_low, fibo_50
    elif prev_price > fibo_50 and current_price < fibo_50:
        return "SELL", swing_high, swing_low, fibo_50
    else:
        return "WAIT", swing_high, swing_low, fibo_50

signal, sw_high, sw_low, fib_50 = get_fibo_signal(df, fibo_length)
current_price = closes[-1]

balance, wins, losses = 1000, 0, 0
bal_history = [1000]
for i in range(fibo_length, len(df)-1):
    window = df.iloc[i-fibo_length:i]
    f50 = (window["high"].max() + window["low"].min()) / 2
    prev_c = df["close"].iloc[i-1]
    curr_c = df["close"].iloc[i]
    next_c = df["close"].iloc[i+1]
    sig = "WAIT"
    if prev_c < f50 and curr_c > f50: sig = "BUY"
    elif prev_c > f50 and curr_c < f50: sig = "SELL"
    if sig!= "WAIT":
        is_win = (next_c > curr_c) if sig == "BUY" else (next_c < curr_c)
        if is_win: wins+=1; balance+=10
        else: losses+=1; balance-=10
        bal_history.append(balance)

total = wins+losses
win_rate = (wins/total*100) if total else 0

st.subheader(f"📊 {selected_market} - 50% Fibo Analysis")
k1,k2,k3,k4 = st.columns(4)
k1.metric("Swing High", f"{sw_high:.2f}")
k2.metric("50% Level", f"{fib_50:.2f}")
k3.metric("Swing Low", f"{sw_low:.2f}")
k4.metric("Current Price", f"{current_price:.2f}")

k1,k2,k3 = st.columns(3)
k1.metric("Trades", total)
k2.metric("Win Rate", f"{win_rate:.1f}%")
k3.metric("Final Balance", f"${balance}", f"{balance-1000}")

fig, ax = plt.subplots(figsize=(12, 4))
ax.plot(df["close"].tail(100), label="Price")
ax.axhline(sw_high, color="red", linestyle="--", label="High")
ax.axhline(sw_low, color="green", linestyle="--", label="Low")
ax.axhline(fib_50, color="gold", linewidth=2, label="50% FIBO")
ax.legend()
ax.grid(True, alpha=0.2)
st.pyplot(fig, use_container_width=True)

st.divider()
if st.button(f"🔮 {selected_market} - 50% Fibo Signal", type="primary", use_container_width=True):
    if signal == "BUY":
        st.success(f"## {selected_market} -> BUY 🟢")
        st.write(f"Price ne 50% Fibo ({fib_50:.2f}) ko upar break kiya")
    elif signal == "SELL":
        st.error(f"## {selected_market} -> SELL 🔴")
        st.write(f"Price ne 50% Fibo ({fib_50:.2f}) ko neeche break kiya")
    else:
        st.warning(f"## {selected_market} -> WAIT ⏸️")
