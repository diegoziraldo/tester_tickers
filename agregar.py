def crear_tab_alertas(parent):

    import tkinter as tk
    from tkinter import ttk, messagebox
    import requests
    from datetime import datetime

    frame = ttk.Frame(parent, padding=15)

    # ==============================
    # CONFIG
    # ==============================

    def cargar_config():
        config = {}
        try:
            with open("datos.txt", "r") as f:
                for linea in f:
                    if "=" in linea:
                        k, v = linea.strip().split("=", 1)
                        config[k.strip()] = v.strip()
        except FileNotFoundError:
            messagebox.showerror("Error", "No se encontró datos.txt")
            return {}
        return config

    config = cargar_config()
    URL = config.get("URL")

    # ==============================
    # FUNCIONES
    # ==============================

    def enviar_datos():
        if not entry_fecha.get() or not entry_tipo.get() or not entry_monto.get() or not entry_ticker.get():
            messagebox.showerror("Error", "Campos obligatorios faltantes")
            return

        try:
            monto = float(entry_monto.get())
        except:
            messagebox.showerror("Error", "Monto inválido")
            return

        data = {
            "action": "create",
            "fecha": entry_fecha.get(),
            "tipo": entry_tipo.get(),
            "monto": monto,
            "ticker": entry_ticker.get(),
            "entrada": entry_entrada.get(),
            "target": entry_target.get(),
            "stop": entry_stop.get(),
            "nota_entrada": entry_nota_entrada.get(),
            "nota_salida": entry_nota_salida.get()
        }

        try:
            r = requests.post(URL, json=data, timeout=10)

            if r.status_code == 200:
                messagebox.showinfo("OK", "Guardado correctamente")
                limpiar()
            else:
                messagebox.showerror("Error", r.text)

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def editar_dato():
        if not entry_id.get():
            messagebox.showerror("Error", "Falta ID")
            return

        data = {
            "action": "update",
            "id": entry_id.get(),
            "fecha": entry_fecha.get(),
            "tipo": entry_tipo.get(),
            "monto": entry_monto.get(),
            "ticker": entry_ticker.get(),
            "entrada": entry_entrada.get(),
            "target": entry_target.get(),
            "stop": entry_stop.get(),
            "nota_entrada": entry_nota_entrada.get(),
            "nota_salida": entry_nota_salida.get()
        }

        try:
            r = requests.post(URL, json=data)
            messagebox.showinfo("Respuesta", r.text)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def borrar_dato():
        if not entry_id.get():
            messagebox.showerror("Error", "Falta ID")
            return

        try:
            r = requests.post(URL, json={"action": "delete", "id": entry_id.get()})
            messagebox.showinfo("Respuesta", r.text)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def limpiar():
        entry_tipo.delete(0, tk.END)
        entry_monto.delete(0, tk.END)
        entry_ticker.delete(0, tk.END)
        entry_entrada.delete(0, tk.END)
        entry_target.delete(0, tk.END)
        entry_stop.delete(0, tk.END)
        entry_nota_entrada.delete(0, tk.END)
        entry_nota_salida.delete(0, tk.END)

        entry_fecha.delete(0, tk.END)
        entry_fecha.insert(0, datetime.now().strftime("%Y-%m-%d"))

    # ==============================
    # UI
    # ==============================

    # ID
    ttk.Label(frame, text="ID").grid(row=0, column=0, sticky="w")
    entry_id = ttk.Entry(frame)
    entry_id.grid(row=0, column=1, sticky="ew", padx=5)

    # Fecha
    ttk.Label(frame, text="Fecha").grid(row=1, column=0, sticky="w")
    entry_fecha = ttk.Entry(frame)
    entry_fecha.grid(row=1, column=1, sticky="ew", padx=5)
    entry_fecha.insert(0, datetime.now().strftime("%Y-%m-%d"))

    # Tipo
    ttk.Label(frame, text="Tipo").grid(row=2, column=0, sticky="w")
    entry_tipo = ttk.Entry(frame)
    entry_tipo.grid(row=2, column=1, sticky="ew", padx=5)

    # Monto
    ttk.Label(frame, text="Monto").grid(row=3, column=0, sticky="w")
    entry_monto = ttk.Entry(frame)
    entry_monto.grid(row=3, column=1, sticky="ew", padx=5)

    # Ticker
    ttk.Label(frame, text="Ticker").grid(row=4, column=0, sticky="w")
    entry_ticker = ttk.Entry(frame)
    entry_ticker.grid(row=4, column=1, sticky="ew", padx=5)

    # Entrada
    ttk.Label(frame, text="Entrada").grid(row=5, column=0, sticky="w")
    entry_entrada = ttk.Entry(frame)
    entry_entrada.grid(row=5, column=1, sticky="ew", padx=5)

    # Target
    ttk.Label(frame, text="Target").grid(row=6, column=0, sticky="w")
    entry_target = ttk.Entry(frame)
    entry_target.grid(row=6, column=1, sticky="ew", padx=5)

    # Stop
    ttk.Label(frame, text="Stop Loss").grid(row=7, column=0, sticky="w")
    entry_stop = ttk.Entry(frame)
    entry_stop.grid(row=7, column=1, sticky="ew", padx=5)

    # Nota entrada
    ttk.Label(frame, text="Nota entrada").grid(row=8, column=0, sticky="w")
    entry_nota_entrada = ttk.Entry(frame)
    entry_nota_entrada.grid(row=8, column=1, sticky="ew", padx=5)

    # Nota salida
    ttk.Label(frame, text="Nota salida").grid(row=9, column=0, sticky="w")
    entry_nota_salida = ttk.Entry(frame)
    entry_nota_salida.grid(row=9, column=1, sticky="ew", padx=5)

    # BOTONES
    btn_frame = ttk.Frame(frame)
    btn_frame.grid(row=10, column=0, columnspan=2, pady=10)

    ttk.Button(btn_frame, text="Guardar", command=enviar_datos).grid(row=0, column=0, padx=5)
    ttk.Button(btn_frame, text="Editar", command=editar_dato).grid(row=0, column=1, padx=5)
    ttk.Button(btn_frame, text="Borrar", command=borrar_dato).grid(row=0, column=2, padx=5)

    # expand horizontal
    frame.columnconfigure(1, weight=1)

    return frame