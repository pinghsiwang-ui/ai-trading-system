import yfinance as yf
import pandas as pd
import numpy as np
import ta
import time

def get_data_safe(ticker, retries=3):
    for i in range(retries):
        try:
            df = yf.download(ticker, period="1y", progress=False)
            if not df.empty:
                return df
        except:
            time.sleep(1)
    return None


def analyze_stock(ticker):
    df = get_data_safe(ticker)

    if df is None or df.empty:
        return None

    df = df.dropna()

    if len(df) < 60:
        return None

    # === 数据统一 ===
    close = df['Close'].squeeze()
    low_series = df['Low'].squeeze()
    high_series = df['High'].squeeze()

    # === 指标 ===
    ma20 = close.rolling(20).mean()
    ma50 = close.rolling(50).mean()
    ma200 = close.rolling(200).mean()

    rsi = ta.momentum.RSIIndicator(close).rsi()
    macd = ta.trend.MACD(close).macd()

    try:
        price = float(close.iloc[-1])
        ma20_last = float(ma20.iloc[-1])
        ma50_last = float(ma50.iloc[-1])
        ma200_last = float(ma200.iloc[-1]) if not pd.isna(ma200.iloc[-1]) else ma50_last

        rsi_last = float(rsi.iloc[-1])
        macd_last = float(macd.iloc[-1])

        low = float(low_series.tail(20).min())
        high = float(high_series.tail(20).max())

    except:
        return None

    # === AI评分系统（升级版） ===
    score = 0

    # 趋势
    if price > ma200_last:
        score += 25
    if price > ma50_last:
        score += 15
    if ma50_last > ma200_last:
        score += 10

    # 动量
    if 50 < rsi_last < 70:
        score += 15
    elif rsi_last < 30:
        score += 10  # 超卖反弹

    if macd_last > 0:
        score += 10

    # 支撑位
    if (price - low) / price < 0.03:
        score += 25

    # 风险惩罚
    if price < ma50_last:
        score -= 10

    return {
        "Ticker": ticker,
        "Price": round(price, 2),
        "Score": score,
        "Support": round(low, 2),
        "Resistance": round(high, 2),
        "RSI": round(rsi_last, 1)
    }

tickers = [
"CLS","GFS","AMZN","AVGO","AMKR","NOK","MU","TSM","AEHR",
"IREN","BE","AAOI","COHR","ANET","MCHP","TXN","ASX",
"ENPH","VPG","NVTS","ON","HIMX","STM"
]

results = []

for t in tickers:
    res = analyze_stock(t)
    if res:
        results.append(res)

df_result = pd.DataFrame(results)

# 排序
df_result = df_result.sort_values(by="Score", ascending=False)

# TOP 5
top5 = df_result.head(5)
