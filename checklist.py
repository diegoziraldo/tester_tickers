from config import estrategias
import pandas as pd

def actualizar_checklist(last, inputs, vars_ui, estrategia_nombre):
    score = 0
    total = 0

    # ==============================
    # SAFE GET (evita errores)
    # ==============================
    def get(key):
        val = last.get(key, None)
        return val if val is not None and pd.notna(val) else None

    # ==============================
    # CHECK SEGURO
    # ==============================
    def check(condicion):
        nonlocal score, total
        total += 1
        if condicion:
            score += 1
            return "✅"
        return "❌"

    # ==============================
    # INPUTS (con protección)
    # ==============================
    try:
        rsi_min = float(inputs["rsi"].get())
        adx_min = float(inputs["adx"].get())
        stoch_max = float(inputs["stoch"].get())
        atr_min_pct = float(inputs["atr"].get()) / 100
    except:
        rsi_min, adx_min, stoch_max, atr_min_pct = 50, 20, 80, 0.01

    close = get("Close")
    ema20 = get("EMA20")
    ema50 = get("EMA50")
    ema200 = get("EMA200")
    rsi = get("RSI")
    macd = get("MACD")
    stoch = get("STOCH")
    adx = get("ADX")
    atr = get("ATR")

    # ==============================
    # CHECKS PRINCIPALES
    # ==============================
    vars_ui["trend"].set(
        f"EMA200 tendencia: {check(close and ema200 and close > ema200)}"
    )

    vars_ui["ema_alignment"].set(
        f"Alineación EMA: {check(ema20 and ema50 and ema200 and ema20 > ema50 > ema200)}"
    )

    vars_ui["rsi"].set(
        f"RSI > {rsi_min}: {check(rsi and rsi > rsi_min)}"
    )

    vars_ui["macd"].set(
        f"MACD > 0: {check(macd and macd > 0)}"
    )

    vars_ui["stoch"].set(
        f"Stoch < {stoch_max}: {check(stoch and stoch < stoch_max)}"
    )

    vars_ui["adx"].set(
        f"ADX > {adx_min}: {check(adx and adx > adx_min)}"
    )

    vars_ui["atr"].set(
        f"ATR OK: {check(atr and close and atr > close * atr_min_pct)}"
    )

    vars_ui["breakout"].set(
        f"Breakout EMA20: {check(close and ema20 and close > ema20)}"
    )

    # ==============================
    # CONFIG DINÁMICA (estrategias)
    # ==============================
    config = estrategias.get(estrategia_nombre, {})

    if "EMA20" in config and ema20:
        vars_ui["ema20"].set(
            f"EMA20 > {config['EMA20']}: {check(ema20 > config['EMA20'])}"
        )

    if "EMA50" in config and ema50:
        vars_ui["ema50"].set(
            f"EMA50 > {config['EMA50']}: {check(ema50 > config['EMA50'])}"
        )

    if "CLOSE" in config and close:
        vars_ui["close"].set(
            f"Close > {config['CLOSE']}: {check(close > config['CLOSE'])}"
        )

    if "MACD" in config and macd:
        vars_ui["macd_param"].set(
            f"MACD > {config['MACD']}: {check(macd > config['MACD'])}"
        )

    # ==============================
    # SCORE FINAL
    # ==============================
    porcentaje = (score / total) * 100 if total > 0 else 0

    if porcentaje >= 85:
        decision = "🔥 SETUP FUERTE"
    elif porcentaje >= 65:
        decision = "🟢 BUEN SETUP"
    elif porcentaje >= 50:
        decision = "⚠️ ACEPTABLE"
    else:
        decision = "❌ EVITAR"

    vars_ui["score"].set(
        f"Score: {score}/{total} ({porcentaje:.0f}%) → {decision}"
    )