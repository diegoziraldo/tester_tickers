from config import estrategias

def actualizar_checklist(last, inputs, vars_ui, estrategia_nombre):
    score = 0
    total = 0

    def check(condicion):
        nonlocal score, total
        total += 1
        if condicion:
            score += 1
            return "✅"
        return "❌"

    rsi_min = float(inputs["rsi"].get())
    adx_min = float(inputs["adx"].get())
    stoch_max = float(inputs["stoch"].get())
    atr_min_pct = float(inputs["atr"].get()) / 100

    vars_ui["trend"].set(f"EMA200 tendencia: {check(last['Close'] > last['EMA200'])}")
    vars_ui["ema_alignment"].set(f"Alineación EMA: {check(last['EMA20'] > last['EMA50'] > last['EMA200'])}")

    vars_ui["rsi"].set(f"RSI > {rsi_min}: {check(last['RSI'] > rsi_min)}")
    vars_ui["macd"].set(f"MACD > 0: {check(last['MACD'] > 0)}")

    vars_ui["stoch"].set(f"Stoch < {stoch_max}: {check(last['STOCH'] < stoch_max)}")
    vars_ui["adx"].set(f"ADX > {adx_min}: {check(last['ADX'] > adx_min)}")

    vars_ui["atr"].set(f"ATR OK: {check(last['ATR'] > last['Close'] * atr_min_pct)}")
    vars_ui["breakout"].set(f"Breakout EMA20: {check(last['Close'] > last['EMA20'])}")

    config = estrategias.get(estrategia_nombre, {})

    if "EMA20" in config:
        vars_ui["ema20"].set(f"EMA20 > {config['EMA20']}: {check(last['EMA20'] > config['EMA20'])}")

    if "EMA50" in config:
        vars_ui["ema50"].set(f"EMA50 > {config['EMA50']}: {check(last['EMA50'] > config['EMA50'])}")

    if "CLOSE" in config:
        vars_ui["close"].set(f"Close > {config['CLOSE']}: {check(last['Close'] > config['CLOSE'])}")

    if "MACD" in config:
        vars_ui["macd_param"].set(f"MACD > {config['MACD']}: {check(last['MACD'] > config['MACD'])}")

    porcentaje = (score / total) * 100 if total > 0 else 0

    decision = "❌ EVITAR"
    if porcentaje >= 80:
        decision = "🔥 SETUP FUERTE"
    elif porcentaje >= 60:
        decision = "⚠️ SETUP ACEPTABLE"

    vars_ui["score"].set(f"Score: {score}/{total} ({porcentaje:.0f}%) → {decision}")