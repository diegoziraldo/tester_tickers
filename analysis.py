import yfinance as yf
import ta
import pandas as pd
import requests
import xml.etree.ElementTree as ET
import webbrowser

# ==============================
# INDICADORES
# ==============================
def calcular_indicadores(df):
    df = df.copy()

    close = df["Close"]
    high = df["High"]
    low = df["Low"]

    df["EMA20"] = ta.trend.ema_indicator(close, 20)
    df["EMA50"] = ta.trend.ema_indicator(close, 50)
    df["EMA200"] = ta.trend.ema_indicator(close, 200)

    df["RSI"] = ta.momentum.rsi(close)
    df["ADX"] = ta.trend.adx(high, low, close)
    df["ATR"] = ta.volatility.average_true_range(high, low, close)

    df["resistencia"] = high.rolling(20).max()
    df["soporte"] = low.rolling(20).min()
    df["vol_mean"] = df["Volume"].rolling(20).mean()

    return df


# ==============================
# DIVERGENCIAS RSI
# ==============================
def detectar_divergencias(df):
    if len(df) < 30:
        return None

    precios = df["Close"].tail(30)
    rsi = df["RSI"].tail(30)

    # últimos 2 picos
    max1 = precios.idxmax()
    max2 = precios.drop(max1).idxmax()

    min1 = precios.idxmin()
    min2 = precios.drop(min1).idxmin()

    divergencia = ""

    # Bearish divergence
    if precios[max1] > precios[max2] and rsi[max1] < rsi[max2]:
        divergencia = "🔴 Divergencia bajista (posible caída)"

    # Bullish divergence
    if precios[min1] < precios[min2] and rsi[min1] > rsi[min2]:
        divergencia = "🟢 Divergencia alcista (posible rebote)"

    return divergencia


# ==============================
# BACKTEST
# ==============================
def backtest(df):
    wins = 0
    total = 0

    for i in range(50, len(df) - 5):
        row = df.iloc[i]

        if row["EMA20"] > row["EMA50"] and row["RSI"] < 40:
            entry = df["Close"].iloc[i]
            future = df["Close"].iloc[i + 5]

            total += 1
            if future > entry:
                wins += 1

    return round((wins / total) * 100, 2) if total > 0 else 0


# ==============================
# ANALISIS PRO MAX
# ==============================
def analizar_logica(df, d, s, m, precio):
    txt = "\n--- ANALISIS PRO MAX ---\n"
    score = 0

    # TENDENCIA
    def tendencia(row):
        if row["EMA20"] > row["EMA50"] > row["EMA200"]:
            return "ALCISTA"
        elif row["EMA20"] < row["EMA50"] < row["EMA200"]:
            return "BAJISTA"
        return "NEUTRA"

    t_d = tendencia(d)
    t_s = tendencia(s)
    t_m = tendencia(m)

    txt += f"\n📅 Diario: {t_d}"
    txt += f"\n📊 Semanal: {t_s}"
    txt += f"\n🏦 Mensual: {t_m}\n"

    if t_d == "ALCISTA": score += 1
    if t_s == "ALCISTA": score += 1
    if t_m == "ALCISTA": score += 1

    # ADX
    if d["ADX"] > 25:
        txt += "\n⚡ Tendencia fuerte"
        score += 1

    # RSI INTELIGENTE
    if d["RSI"] > 70:
        if d["ADX"] > 25:
            txt += "\n🔥 Sobrecompra en tendencia fuerte (continuación)"
        else:
            txt += "\n🔴 Sobrecompra débil (riesgo)"
            score -= 2

    elif d["RSI"] < 30:
        txt += "\n🟢 Sobreventa"
        score += 1

    # DISTANCIA EMA
    dist = (precio - d["EMA20"]) / d["EMA20"]
    if dist > 0.05:
        txt += "\n⚠️ Muy extendido"
        score -= 1

    # SOPORTE / RESISTENCIA
    if precio >= d["resistencia"] * 0.98:
        txt += "\n🚧 En resistencia"
        score -= 1
    elif precio <= d["soporte"] * 1.02:
        txt += "\n🟢 En soporte"
        score += 1

    # VOLUMEN
    if d["Volume"] > d["vol_mean"]:
        txt += "\n📈 Volumen fuerte"
        score += 1

    # SETUPS
    setup = "NINGUNO"

    if abs(precio - d["EMA20"]) / d["EMA20"] < 0.02 and t_d == "ALCISTA":
        setup = "PULLBACK"
        score += 1

    if precio > d["resistencia"]:
        setup = "BREAKOUT"
        score += 1

    txt += f"\n\n🎯 Setup: {setup}"

    # DIVERGENCIAS
    div = detectar_divergencias(df)
    if div:
        txt += f"\n{div}"
        if "bajista" in div:
            score -= 2
        elif "alcista" in div:
            score += 1

    # RISK MANAGEMENT
    stop = precio - d["ATR"]
    target = precio + (d["ATR"] * 2)
    rr = (target - precio) / (precio - stop)

    txt += f"\n🛑 Stop: {stop:.2f}"
    txt += f"\n💰 Target: {target:.2f}"
    txt += f"\n⚖️ R/R: {rr:.2f}"

    # BACKTEST
    winrate = backtest(df)
    txt += f"\n📊 Winrate: {winrate}%"

    # RESULTADO FINAL
    txt += "\n\n--- RESULTADO ---\n"

    if score >= 5:
        señal = "🟢 BUY FUERTE"
    elif score >= 3:
        señal = "🟡 BUY"
    elif score >= 1:
        señal = "🟡 WAIT"
    else:
        señal = "🔴 SELL"

    txt += señal
    txt += f"\nScore: {score}/10\n"

    return txt


# ==============================
# NOTICIAS
# ==============================
def obtener_noticias_google(ticker):
    noticias = []

    try:
        url = f"https://news.google.com/rss/search?q={ticker}&hl=es-419&gl=AR&ceid=AR:es-419"
        r = requests.get(url, timeout=10)
        root = ET.fromstring(r.content)

        for item in root.findall(".//item")[:5]:
            noticias.append((
                item.find("title").text,
                item.find("link").text
            ))
    except:
        noticias.append(("Error noticias", ""))

    return noticias


# ==============================
# FUNDAMENTALES
# ==============================
def obtener_fundamentales(ticker):
    try:
        t = yf.Ticker(ticker)
        info = t.info

        return f"""
--- FUNDAMENTALES ---
Empresa: {info.get("longName")}
Sector: {info.get("sector")}
P/E: {info.get("trailingPE")}
ROE: {info.get("returnOnEquity")}
"""
    except:
        return "\n❌ Error fundamentales\n"


# ==============================
# MAIN
# ==============================
def analizar_ticker(ticker):
    df = yf.download(ticker, period="5y", auto_adjust=True, progress=False)

    if df.empty:
        return None, "❌ Ticker inválido"

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df = df.dropna()
    df = calcular_indicadores(df)

    semanal = df.resample("W").last()
    mensual = df.resample("ME").last()

    d = df.iloc[-1]
    s = semanal.iloc[-1]
    m = mensual.iloc[-1]

    precio = float(d["Close"])

    result = f"\n===== {ticker} =====\nPrecio: {precio:.2f}\n"
    result += analizar_logica(df, d, s, m, precio)
    result += obtener_fundamentales(ticker)

    return d, result


# ==============================
# TKINTER
# ==============================
def mostrar_resultado(text_widget, result, noticias):
    text_widget.config(state="normal")
    text_widget.delete("1.0", "end")

    text_widget.insert("end", result + "\n\n--- NOTICIAS ---\n\n")

    for i, (titulo, link) in enumerate(noticias):
        tag = f"link{i}"

        text_widget.insert("end", f"📰 {titulo}\n", tag)
        text_widget.tag_config(tag, foreground="blue", underline=True)

        def callback(event, url=link):
            webbrowser.open(url)

        text_widget.tag_bind(tag, "<Button-1>", callback)
        text_widget.tag_bind(tag, "<Enter>", lambda e: text_widget.config(cursor="hand2"))
        text_widget.tag_bind(tag, "<Leave>", lambda e: text_widget.config(cursor=""))

        text_widget.insert("end", "\n")

    text_widget.config(state="disabled")