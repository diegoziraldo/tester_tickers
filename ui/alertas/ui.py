import tkinter as tk
from tkinter import ttk, messagebox
import threading

from ui.alertas.tab_alertas import crear_tab_alertas
from sheets import cargar_estrategias_desde_sheets
from analysis import analizar_ticker
from checklist import actualizar_checklist


class TradingApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Trading Pro")
        self.root.geometry("900x700")

        self.cargando = False

        self.init_variables()
        self.build_ui()
        self.init_data()

    # ==============================
    # VARIABLES
    # ==============================

    def init_variables(self):
        self.rsi_input = tk.StringVar(value="55")
        self.adx_input = tk.StringVar(value="25")
        self.stoch_input = tk.StringVar(value="80")
        self.atr_input = tk.StringVar(value="1")

        self.vars_ui = {
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

        self.inputs = {
            "rsi": self.rsi_input,
            "adx": self.adx_input,
            "stoch": self.stoch_input,
            "atr": self.atr_input
        }

    # ==============================
    # UI
    # ==============================

    def build_ui(self):
        self.build_top()
        self.build_tabs()

    def build_top(self):
        top_frame = ttk.Frame(self.root)
        top_frame.pack(pady=5)

        ttk.Label(top_frame, text="Ticker").pack()

        self.ticker_select = ttk.Entry(top_frame)
        self.ticker_select.pack()
        self.ticker_select.bind("<Return>", lambda e: self.analizar())

        ttk.Button(top_frame, text="Analizar", command=self.analizar).pack(pady=5)

    def build_tabs(self):
        notebook = ttk.Notebook(self.root)
        notebook.pack(expand=True, fill="both")

        self.build_tab_analizador(notebook)
        self.build_tab_checklist(notebook)
        self.build_tab_alertas(notebook)

    def build_tab_analizador(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Analizador")

        self.output = tk.Text(frame)
        self.output.pack(expand=True, fill="both")

    def build_tab_checklist(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Checklist PRO")

        ttk.Label(frame, text="Estrategia").pack(anchor="w", padx=10)

        self.estrategia_select = ttk.Combobox(frame)
        self.estrategia_select.pack(padx=10, pady=5)
        self.estrategia_select.bind("<<ComboboxSelected>>", self.cargar_estrategia)

        ttk.Button(
            frame,
            text="🔄 Actualizar Estrategias",
            command=self.actualizar_estrategias
        ).pack(pady=5)

        config_frame = ttk.LabelFrame(frame, text="Parámetros")
        config_frame.pack(padx=10, pady=10, fill="x")

        ttk.Label(config_frame, text="RSI mínimo").grid(row=0, column=0)
        ttk.Entry(config_frame, textvariable=self.rsi_input, width=5).grid(row=0, column=1)

        ttk.Label(config_frame, text="ADX mínimo").grid(row=1, column=0)
        ttk.Entry(config_frame, textvariable=self.adx_input, width=5).grid(row=1, column=1)

        ttk.Label(config_frame, text="Stoch máximo").grid(row=2, column=0)
        ttk.Entry(config_frame, textvariable=self.stoch_input, width=5).grid(row=2, column=1)

        ttk.Label(config_frame, text="ATR % mínimo").grid(row=3, column=0)
        ttk.Entry(config_frame, textvariable=self.atr_input, width=5).grid(row=3, column=1)

        for key in [
            "trend", "ema_alignment", "rsi", "macd",
            "stoch", "adx", "atr", "breakout",
            "ema20", "ema50", "close", "macd_param"
        ]:
            ttk.Label(frame, textvariable=self.vars_ui[key]).pack(anchor="w", padx=10)

        ttk.Separator(frame).pack(fill="x", pady=10)

        ttk.Label(
            frame,
            textvariable=self.vars_ui["score"],
            font=("Arial", 12, "bold")
        ).pack(anchor="w", padx=10)

    def build_tab_alertas(self, notebook):
        frame_alertas = crear_tab_alertas(notebook)
        notebook.add(frame_alertas, text="Alertas")

    # ==============================
    # LOGICA
    # ==============================

    def analizar(self, force=False):
        if self.cargando:
            return

        ticker = self.ticker_select.get().strip().upper()

        if not ticker:
            self.mostrar_output("⚠ Ingresá un ticker válido\n")
            return

        self.cargando = True
        self.set_loading(True)
        self.mostrar_output("⏳ Analizando...\n")

        def worker():
            try:
                last, result = analizar_ticker(ticker)

                self.root.after(0, lambda: self.actualizar_resultado(last, result))

            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
            finally:
                self.root.after(0, self.fin_carga)

        threading.Thread(target=worker, daemon=True).start()

    def actualizar_resultado(self, last, result):
        self.mostrar_output(result)

        if last:
            actualizar_checklist(
                last,
                self.inputs,
                self.vars_ui,
                self.estrategia_select.get()
            )

    def cargar_estrategia(self, event=None):
        from config import estrategias

        nombre = self.estrategia_select.get()

        if nombre in estrategias:
            config = estrategias[nombre]

            if "RSI" in config:
                self.rsi_input.set(str(config["RSI"]))

            if "ADX" in config:
                self.adx_input.set(str(config["ADX"]))

            if "STOCH" in config:
                self.stoch_input.set(str(config["STOCH"]))

            if "ATR" in config:
                self.atr_input.set(str(config["ATR"]))

        self.analizar(force=True)

    def actualizar_estrategias(self):
        self.set_loading(True)

        def worker():
            try:
                cargar_estrategias_desde_sheets(
                    self.estrategia_select,
                    self.root,
                    self.cargar_estrategia
                )
            finally:
                self.root.after(0, self.set_loading, False)

        threading.Thread(target=worker, daemon=True).start()

    # ==============================
    # HELPERS UI
    # ==============================

    def mostrar_output(self, texto):
        self.output.delete("1.0", tk.END)
        self.output.insert(tk.END, texto)

    def set_loading(self, estado):
        self.root.config(cursor="watch" if estado else "")

    def fin_carga(self):
        self.cargando = False
        self.set_loading(False)

    # ==============================
    # INIT DATA
    # ==============================

    def init_data(self):
        self.actualizar_estrategias()


# ==============================
# ENTRYPOINT
# ==============================

def iniciar_app():
    root = tk.Tk()
    app = TradingApp(root)
    root.mainloop()