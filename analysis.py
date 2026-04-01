import yfinance as yf
import ta
import pandas as pd
import requests
import xml.etree.ElementTree as ET

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

    # 🔥 MACD AGREGADO
    df["MACD"] = ta.trend.macd(close)
    df["MACD_signal"] = ta.trend.macd_signal(close)
    df["MACD_diff"] = ta.trend.macd_diff(close)

    df["resistencia"] = high.rolling(20).max()
    df["soporte"] = low.rolling(20).min()
    df["vol_mean"] = df["Volume"].rolling(20).mean()

    return df


# ==============================
# 🔥 FUNDAMENTALES
# ==============================
def obtener_fundamentales(ticker):
    try:
        t = yf.Ticker(ticker)
        info = t.info

        txt = "\n\n--- 📊 FUNDAMENTALES ---\n"

        if info.get("trailingPE"):
            txt += f"PER: {info.get('trailingPE')}\n"

        if info.get("trailingEps"):
            txt += f"EPS: {info.get('trailingEps')}\n"

        if info.get("returnOnEquity"):
            txt += f"ROE: {info.get('returnOnEquity')}\n"

        if info.get("debtToEquity"):
            txt += f"Deuda/Capital: {info.get('debtToEquity')}\n"

        if info.get("profitMargins"):
            txt += f"Margen: {info.get('profitMargins')}\n"

        if info.get("totalRevenue"):
            txt += f"Ingresos: {info.get('totalRevenue')}\n"

        if info.get("revenueGrowth"):
            txt += f"Crecimiento: {info.get('revenueGrowth')}\n"

        return txt

    except:
        return "\n❌ No se pudieron obtener fundamentales\n"


# ==============================
# 🔥 EVALUACION DE INDICADORES
# ==============================
def evaluar_indicadores_pro(d, precio):
    txt = "\n\n--- 🧠 EVALUACION DE INDICADORES ---\n"

    # ==============================
    # 🔥 DETALLE DE EMAs
    # ==============================
    txt += "\n--- 📊 DETALLE DE EMAs ---\n"

    txt += f"EMA20: {d['EMA20']:.2f} → "
    if d["EMA20"] > precio:
        txt += "👎 Por encima del precio\n"
    else:
        txt += "👍 Por debajo del precio\n"

    txt += f"EMA50: {d['EMA50']:.2f} → "
    if d["EMA50"] > precio:
        txt += "👎 Por encima del precio\n"
    else:
        txt += "👍 Por debajo del precio\n"

    txt += f"EMA200: {d['EMA200']:.2f} → "
    if d["EMA200"] > precio:
        txt += "👎 Por encima del precio\n"
    else:
        txt += "👍 Por debajo del precio\n"
    
    txt += "\n\n"

    # EMA
    if d["EMA20"] > d["EMA50"] > d["EMA200"]:
        txt += "✅ EMAs alineadas → tendencia sana\n"
    elif d["EMA20"] < d["EMA50"]:
        txt += "❌ EMAs débiles → tendencia dudosa\n"
    else:
        txt += "⚠️ EMAs sin claridad\n"

    # RSI
    if d["RSI"] > 70:
        txt += "⚠️ RSI en sobrecompra → riesgo de caída\n"
    elif d["RSI"] < 30:
        txt += "✅ RSI en sobreventa → oportunidad\n"
    elif 40 < d["RSI"] < 60:
        txt += "⚠️ RSI neutro → sin ventaja\n"
    else:
        txt += "✅ RSI en zona saludable\n"

    # 🔥 MACD (YA FUNCIONA)
    if "MACD" in d and pd.notna(d["MACD"]):
        if d["MACD"] > 0:
            txt += "✅ MACD positivo → momentum alcista\n"
        elif d["MACD"] < 0:
            txt += "❌ MACD negativo → momentum bajista\n"

    # ADX
    if d["ADX"] > 25:
        txt += "✅ ADX fuerte → tendencia válida\n"
    else:
        txt += "❌ ADX débil → mercado lateral\n"

    # ATR
    atr_pct = d["ATR"] / precio
    if atr_pct > 0.03:
        txt += "⚠️ ATR alto → volatilidad elevada\n"
    elif atr_pct < 0.01:
        txt += "❌ ATR bajo → poco movimiento\n"
    else:
        txt += "✅ ATR óptimo\n"

    # SOPORTE / RESISTENCIA
    if precio >= d["resistencia"] * 0.98:
        txt += "⚠️ Precio en resistencia → mala zona de compra\n"
    elif precio <= d["soporte"] * 1.02:
        txt += "✅ Precio en soporte → buena zona\n"

    # VOLUMEN
    if d["Volume"] > d["vol_mean"]:
        txt += "✅ Volumen confirma movimiento\n"
    else:
        txt += "❌ Volumen débil\n"

    return txt


# ==============================
# ENTRADA PRO
# ==============================
def calcular_entrada_pro(df):
    d = df.iloc[-1]
    prev = df.iloc[-2]

    precio = d["Close"]

    tendencia = d["EMA20"] > d["EMA50"] > d["EMA200"]
    cerca_ema = abs(precio - d["EMA20"]) / d["EMA20"] < 0.02
    rsi_rebote = d["RSI"] > prev["RSI"]
    vela_alcista = d["Close"] > d["Open"]

    if tendencia and cerca_ema and rsi_rebote and vela_alcista:
        return precio, "CONFIRMADA"

    return d["EMA20"], "ESPERA"


# ==============================
# DIVERGENCIAS
# ==============================
def detectar_divergencias(df):
    if len(df) < 30:
        return None

    precios = df["Close"].tail(30)
    rsi = df["RSI"].tail(30)

    max1 = precios.idxmax()
    max2 = precios.drop(max1).idxmax()

    min1 = precios.idxmin()
    min2 = precios.drop(min1).idxmin()

    if precios[max1] > precios[max2] and rsi[max1] < rsi[max2]:
        return "🔴 Divergencia bajista → debilidad en la suba"

    if precios[min1] < precios[min2] and rsi[min1] > rsi[min2]:
        return "🟢 Divergencia alcista → posible rebote"

    return None


# ==============================
# BACKTEST
# ==============================
def backtest_pro(df, rr=3, riesgo_por_trade=0.01):
    capital = 10000
    wins = 0
    losses = 0
    trades = 0

    for i in range(50, len(df) - 10):
        row = df.iloc[i]

        if row["EMA20"] > row["EMA50"] and row["RSI"] < 40:

            entry = df["Close"].iloc[i]
            atr = row["ATR"]

            if pd.isna(atr) or atr == 0:
                continue

            stop = entry - atr
            target = entry + (atr * rr)

            resultado = None

            for j in range(i + 1, i + 10):
                if df["High"].iloc[j] >= target:
                    resultado = "win"
                    break
                if df["Low"].iloc[j] <= stop:
                    resultado = "loss"
                    break

            if resultado is None:
                continue

            trades += 1

            if resultado == "win":
                capital += capital * riesgo_por_trade * rr
                wins += 1
            else:
                capital -= capital * riesgo_por_trade
                losses += 1

    winrate = (wins / trades) * 100 if trades > 0 else 0

    return {
        "winrate": round(winrate, 2),
        "trades": trades,
        "capital_final": round(capital, 2)
    }

# ==============================
# 🔥 DECISION INTELIGENTE FINAL
# ==============================
def decision_inteligente(d, precio):
    score = 0
    razones = []

    # 📈 TENDENCIA (EMAs)
    if d["EMA20"] > d["EMA50"] > d["EMA200"]:
        score += 2
        razones.append("Tendencia alcista fuerte")
    elif d["EMA20"] < d["EMA50"] < d["EMA200"]:
        score -= 2
        razones.append("Tendencia bajista fuerte")

    # ⚡ MOMENTUM (MACD)
    if "MACD" in d and "MACD_signal" in d:
        if d["MACD"] > d["MACD_signal"]:
            score += 2
            razones.append("MACD alcista")
        elif d["MACD"] < d["MACD_signal"]:
            score -= 2
            razones.append("MACD bajista")

    # 💪 FUERZA (ADX)
    if d["ADX"] > 25:
        score += 1
        razones.append("Tendencia con fuerza")
    else:
        score -= 1
        razones.append("Mercado lateral")

    # 🎯 RSI (TIMING)
    if d["RSI"] < 30:
        score += 2
        razones.append("Sobreventa (rebote)")
    elif d["RSI"] > 70:
        score -= 2
        razones.append("Sobrecompra (riesgo)")

    # 📊 VOLUMEN
    if d["Volume"] > d["vol_mean"]:
        score += 1
        razones.append("Volumen acompaña")
    else:
        score -= 1
        razones.append("Volumen débil")

    # 🧱 SOPORTE / RESISTENCIA
    if precio <= d["soporte"] * 1.02:
        score += 1
        razones.append("Zona de soporte")
    elif precio >= d["resistencia"] * 0.98:
        score -= 1
        razones.append("Zona de resistencia")

    # 🕯️ VELA
    if d["Close"] > d["Open"]:
        score += 1
        razones.append("Vela alcista")
    else:
        score -= 1
        razones.append("Vela bajista")

    # ==========================
    # 🎯 DECISION FINAL
    # ==========================
    if score >= 5:
        decision = "🟢 COMPRAR FUERTE"
    elif score >= 2:
        decision = "🟢 COMPRAR"
    elif score >= -1:
        decision = "🟡 ESPERAR"
    else:
        decision = "🔴 VENDER"

    txt = "\n\n--- 🤖 DECISION INTELIGENTE ---\n"
    txt += f"Score: {score}\n"
    txt += f"Acción: {decision}\n"
    txt += "Factores:\n"

    for r in razones:
        txt += f"- {r}\n"

    return txt




# ==============================
# ANALISIS + EXPLICACION
# ==============================
def analizar_logica(df, d, s, m, precio):
    txt = "\n--- ANALISIS PRO ---\n"
    score = 0
    razones = []

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

    if t_d == "ALCISTA":
        score += 2
        razones.append("Tendencia diaria alcista")

    if t_s == "ALCISTA":
        score += 1
        razones.append("Tendencia semanal acompaña")

    if d["ADX"] > 25:
        score += 1
        razones.append("Tendencia fuerte (ADX)")

    if d["RSI"] < 35:
        score += 1
        razones.append("RSI en zona de rebote")

    if d["Volume"] > d["vol_mean"]:
        score += 1
        razones.append("Volumen fuerte confirma movimiento")

    setup = "NINGUNO"
    if abs(precio - d["EMA20"]) / d["EMA20"] < 0.02:
        setup = "PULLBACK"
        score += 1
        razones.append("Pullback a EMA20")

    if precio > d["resistencia"]:
        setup = "BREAKOUT"
        score += 1
        razones.append("Ruptura de resistencia")

    txt += f"\n🎯 Setup: {setup}"

    div = detectar_divergencias(df)
    if div:
        txt += f"\n{div}"

    entrada, tipo = calcular_entrada_pro(df)

    stop = entrada - d["ATR"]
    target = entrada + (d["ATR"] * 3)

    txt += f"\n\n🚀 Entrada: {entrada:.2f}"
    txt += f"\n🎯 Tipo: {tipo}"
    txt += f"\n🛑 Stop: {stop:.2f}"
    txt += f"\n💰 Target: {target:.2f}"

    stats = backtest_pro(df)

    txt += f"\n\n📊 Winrate: {stats['winrate']}%"
    txt += f"\n💰 Capital final: {stats['capital_final']}"

    txt += evaluar_indicadores_pro(d, precio)

    txt += "\n\n--- DECISION ---\n"

    if score >= 7:
        txt += "🟢 BUY FUERTE\n"
    elif score >= 5:
        txt += "🟡 BUY\n"
    elif score >= 3:
        txt += "🟡 WAIT\n"
    else:
        txt += "🔴 SELL\n"

    txt += "\n📌 Factores:\n"
    for r in razones:
        txt += f"- {r}\n"

    txt += decision_inteligente(d, precio)
    
    return txt

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

    # 🔥 FUNDAMENTALES AGREGADOS
    result += obtener_fundamentales(ticker)

    result += analizar_logica(df, d, s, m, precio)

    return d, result