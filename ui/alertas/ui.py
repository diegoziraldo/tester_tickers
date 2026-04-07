import tkinter as tk
from tkinter import ttk, messagebox

from ui.alertas.tab_alertas import crear_tab_alertas # 👈 IMPORTANTE (tu archivo real)
from config import ultimo_ticker, ultimo_data
from sheets import cargar_estrategias_desde_sheets
from analysis import analizar_ticker
from checklist import actualizar_checklist


def iniciar_app():

    # ==============================
    # ROOT
    # ==============================
    root = tk.Tk()
    root.title("Trading Pro")
    root.geometry("900x700")

    # ==============================
    # VARIABLES UI
    # ==============================

    rsi_input = tk.StringVar(value="55")
    adx_input = tk.StringVar(value="25")
    stoch_input = tk.StringVar(value="80")
    atr_input = tk.StringVar(value="1")

    vars_ui = {
        "trend": tk.StringVar(),
        "ema_alignment": tk.StringVar(),
        "rsi": tk.StringVar(),
        "macd": tk.StringVar(),
        "stoch": tk.StringVar(),
        "adx": tk.StringVar(),
        "atr": tk.StringVar(),
        "breakout": tk.StringVar(),
        "ema20": tk.StringVar(),
        "ema50": tk.StringVar(),
        "close": tk.StringVar(),
        "macd_param": tk.StringVar(),
        "score": tk.StringVar()
    }

    inputs = {
        "rsi": rsi_input,
        "adx": adx_input,
        "stoch": stoch_input,
        "atr": atr_input
    }

    # ==============================
    # FUNCIONES
    # ==============================

    def analizar(force=False):
        ticker = ticker_select.get().strip().upper()

        if not ticker:
            output.delete("1.0", tk.END)
            output.insert(tk.END, "⚠ Ingresá un ticker válido\n")
            return

        last, result = analizar_ticker(ticker)

        if last is None:
            output.delete("1.0", tk.END)
            output.insert(tk.END, result)
            return

        output.delete("1.0", tk.END)
        output.insert(tk.END, result)

        actualizar_checklist(
            last,
            inputs,
            vars_ui,
            estrategia_select.get()
        )

    def cargar_estrategia(event=None):
        from config import estrategias

        nombre = estrategia_select.get()

        if nombre in estrategias:
            config = estrategias[nombre]

            if "RSI" in config:
                rsi_input.set(str(config["RSI"]))

            if "ADX" in config:
                adx_input.set(str(config["ADX"]))

            if "STOCH" in config:
                stoch_input.set(str(config["STOCH"]))

            if "ATR" in config:
                atr_input.set(str(config["ATR"]))

        analizar(force=True)

    # ==============================
    # UI
    # ==============================

    top_frame = ttk.Frame(root)
    top_frame.pack()

    ttk.Label(top_frame, text="Ticker").pack()
    ticker_select = ttk.Entry(top_frame)
    ticker_select.pack()

    ticker_select.bind("<Return>", lambda event: analizar())

    ttk.Button(top_frame, text="Analizar", command=analizar).pack()

    notebook = ttk.Notebook(root)
    notebook.pack(expand=True, fill="both")

    # ==============================
    # TAB ANALIZADOR
    # ==============================

    frame_analizar = ttk.Frame(notebook)
    notebook.add(frame_analizar, text="Analizador")

    output = tk.Text(frame_analizar)
    output.pack(expand=True, fill="both")

    # ==============================
    # TAB CHECKLIST
    # ==============================

    frame_checklist = ttk.Frame(notebook)
    notebook.add(frame_checklist, text="Checklist PRO")

    ttk.Label(frame_checklist, text="Estrategia").pack(anchor="w", padx=10)

    estrategia_select = ttk.Combobox(frame_checklist)
    estrategia_select.pack(padx=10, pady=5)
    estrategia_select.bind("<<ComboboxSelected>>", cargar_estrategia)

    ttk.Button(
        frame_checklist,
        text="🔄 Actualizar Estrategias",
        command=lambda: cargar_estrategias_desde_sheets(
            estrategia_select,
            root,
            cargar_estrategia
        )
    ).pack(pady=5)

    config_frame = ttk.LabelFrame(frame_checklist, text="Parámetros")
    config_frame.pack(padx=10, pady=10, fill="x")

    ttk.Label(config_frame, text="RSI mínimo").grid(row=0, column=0)
    ttk.Entry(config_frame, textvariable=rsi_input, width=5).grid(row=0, column=1)

    ttk.Label(config_frame, text="ADX mínimo").grid(row=1, column=0)
    ttk.Entry(config_frame, textvariable=adx_input, width=5).grid(row=1, column=1)

    ttk.Label(config_frame, text="Stoch máximo").grid(row=2, column=0)
    ttk.Entry(config_frame, textvariable=stoch_input, width=5).grid(row=2, column=1)

    ttk.Label(config_frame, text="ATR % mínimo").grid(row=3, column=0)
    ttk.Entry(config_frame, textvariable=atr_input, width=5).grid(row=3, column=1)

    for key in [
        "trend", "ema_alignment", "rsi", "macd",
        "stoch", "adx", "atr", "breakout",
        "ema20", "ema50", "close", "macd_param"
    ]:
        ttk.Label(frame_checklist, textvariable=vars_ui[key]).pack(anchor="w", padx=10)

    ttk.Separator(frame_checklist).pack(fill="x", pady=10)

    ttk.Label(
        frame_checklist,
        textvariable=vars_ui["score"],
        font=("Arial", 12, "bold")
    ).pack(anchor="w", padx=10)

    # ==============================
    # TAB ALERTAS (TU SISTEMA REAL)
    # ==============================

    frame_alertas = crear_tab_alertas(notebook)
    notebook.add(frame_alertas, text="Alertas")

    # ==============================
    # INIT
    # ==============================

    cargar_estrategias_desde_sheets(
        estrategia_select,
        root,
        cargar_estrategia
    )

    root.mainloop()