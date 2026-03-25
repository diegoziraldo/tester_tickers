import yfinance as yf
import ta
import pandas as pd

def analizar_ticker(ticker):
    data = yf.download(ticker, period="1y", auto_adjust=True, progress=False)

    if data is None or data.empty:
        return None, "❌ Ticker inválido"

    # 🔥 FIX IMPORTANTE: evitar columnas multi-index
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    # 🔥 FIX: asegurar que sean Series (1D)
    close = data["Close"]
    high = data["High"]
    low = data["Low"]

    if isinstance(close, pd.DataFrame):
        close = close.squeeze()
    if isinstance(high, pd.DataFrame):
        high = high.squeeze()
    if isinstance(low, pd.DataFrame):
        low = low.squeeze()

    # ==============================
    # INDICADORES
    # ==============================

    data["EMA20"] = ta.trend.ema_indicator(close, window=20)
    data["EMA50"] = ta.trend.ema_indicator(close, window=50)
    data["EMA200"] = ta.trend.ema_indicator(close, window=200)
    data["RSI"] = ta.momentum.rsi(close)
    data["MACD"] = ta.trend.macd(close)
    data["ADX"] = ta.trend.adx(high, low, close)
    data["ATR"] = ta.volatility.average_true_range(high, low, close)
    data["STOCH"] = ta.momentum.stoch(high, low, close)

    last = data.iloc[-1]

    # ==============================
    # OUTPUT
    # ==============================

    result = f"\n===== {ticker} =====\n\n"
    result += f"Precio: {float(close.iloc[-1]):.2f}\n\n"

    for col in data.columns:
        try:
            val = last[col]
            if pd.notna(val):
                result += f"{col}: {float(val):.2f}\n"
        except:
            pass

    return last, result