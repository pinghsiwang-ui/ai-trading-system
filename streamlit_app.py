import yfinance as yf
import pandas as pd
import ta
import streamlit as st
import plotly.graph_objects as go

st.set_page_config(layout="wide")

st.title("🧠 AI量化交易系统（网页版）")

tickers = [
"CLS","GFS","AMZN","AVGO","AMKR","NOK","MU","TSM","AEHR","IREN",
"BE","AAOI","COHR","ANET","MCHP","TXN","ASX","ENPH","VPG","NVTS",
"ON","HIMX","STM"
]

selected = st.selectbox("选择股票", tickers)

df = yf.download(selected, period="6mo", interval="1d")

df['MA20'] = df['Close'].rolling(20).mean()
df['MA50'] = df['Close'].rolling(50).mean()
df['MA200'] = df['Close'].rolling(200).mean()

df['RSI'] = ta.momentum.RSIIndicator(df['Close']).rsi()
macd = ta.trend.MACD(df['Close'])
df['MACD'] = macd.macd()

price = df['Close'].iloc[-1]
low = df['Low'].tail(20).min()
high = df['High'].tail(20).max()

score = 0

if price > df['MA200'].iloc[-1]:
    score += 25
elif price > df['MA50'].iloc[-1]:
    score += 15

if (price - low)/price < 0.03:
    score += 25

rsi = df['RSI'].iloc[-1]
if rsi < 30:
    score += 15
elif rsi < 40:
    score += 10

if df['MACD'].iloc[-1] > 0:
    score += 15

if df['Volume'].iloc[-1] > df['Volume'].rolling(20).mean().iloc[-1]:
    score += 20

win_rate = min(95, score)
position = int(score / 20) * 10

fig = go.Figure()

fig.add_trace(go.Candlestick(
    x=df.index,
    open=df['Open'],
    high=df['High'],
    low=df['Low'],
    close=df['Close']
))

fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], name="MA20"))
fig.add_trace(go.Scatter(x=df.index, y=df['MA50'], name="MA50"))
fig.add_trace(go.Scatter(x=df.index, y=df['MA200'], name="MA200"))

# 买点区
fig.add_hrect(y0=low, y1=low*1.03, fillcolor="green", opacity=0.2)

# 风险区
fig.add_hrect(y0=high*0.97, y1=high, fillcolor="red", opacity=0.2)

st.plotly_chart(fig, use_container_width=True)

st.subheader("🧠 AI决策")

st.metric("AI评分", score)
st.metric("胜率", f"{win_rate}%")
st.metric("建议仓位", f"{position}%")

if score >= 80:
    st.success("🔥 强烈买入区")
elif score >= 60:
    st.warning("⚠️ 观察区")
else:
    st.error("❌ 不建议")

# 扫描
if st.button("🚀 扫描TOP 5"):
    results = []

    for t in tickers:
        d = yf.download(t, period="6mo", interval="1d", progress=False)
        if d.empty:
            continue

        p = d['Close'].iloc[-1]
        l = d['Low'].tail(20).min()
        r = ta.momentum.RSIIndicator(d['Close']).rsi().iloc[-1]

        s = 0
        if (p-l)/p < 0.03: s += 30
        if r < 30: s += 30

        results.append({"Ticker": t, "Score": s})

    df_res = pd.DataFrame(results).sort_values(by="Score", ascending=False)

    st.subheader("🏆 TOP 5")
    st.dataframe(df_res.head(5))
