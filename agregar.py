def crear_tab_alertas(parent):

    import tkinter as tk
    from tkinter import ttk, messagebox
    import requests
    from datetime import datetime
    import os
    import sys
    import uuid

    frame = ttk.Frame(parent, padding=15)

    # ==============================
    # CONFIG
    # ==============================

    def obtener_ruta_config():
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_path, "datos.txt")

    def cargar_config():
        config = {}
        ruta = obtener_ruta_config()

        if not os.path.exists(ruta):
            messagebox.showerror("Error", f"No existe datos.txt en:\n{ruta}")
            return {}

        with open(ruta, "r") as f:
            for linea in f:
                if "=" in linea:
                    k, v = linea.strip().split("=", 1)
                    config[k.strip()] = v.strip()

        return config

    config = cargar_config()
    URL = config.get("URL")

    if not URL:
        messagebox.showerror("Error", "URL no definida en datos.txt")

    # ==============================
    # FORMATO FECHA
    # ==============================

    def formatear_fecha(dt=None):
        if dt is None:
            dt = datetime.now()
        return dt.strftime("%d/%m/%Y")

    def normalizar_fecha(fecha):
        try:
            return datetime.fromisoformat(fecha).strftime("%d/%m/%Y")
        except:
            return fecha

    # ==============================
    # FUNCIONES
    # ==============================

    def obtener_id_seleccionado():
        sel = tree.selection()
        if not sel:
            return None
        return sel[0]

    def cargar_listado():
        try:
            r = requests.post(URL, json={"action": "read_para_app"}, timeout=10)

            data = r.json()
            print(data)  # 👈 ACÁ

            if not isinstance(data, list):
                messagebox.showerror("Error", f"Respuesta inválida: {data}")
                return

            # 🔴 VALIDACIÓN AGREGADA (ÚNICO CAMBIO)
            if not isinstance(data, list):
                messagebox.showerror("Error", f"Respuesta inválida: {data}")
                return

            for item in tree.get_children():
                tree.delete(item)

            for row in data:
                row_id = row.get("id")

                if row_id is None:
                    row_id = str(uuid.uuid4())

                tree.insert("", "end", iid=str(row_id), values=(
                    row.get("ticker"),
                    normalizar_fecha(row.get("fecha")),
                    row.get("tipo"),
                    row.get("monto"),
                    row.get("entrada"),
                    row.get("target"),
                    row.get("stop"),
                    row.get("nota_entrada"),
                    row.get("nota_salida")
                ))

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def enviar_datos():

        try:
            monto = entry_monto.get()
            monto = float(monto) if monto else None
        except:
            messagebox.showerror("Error", "Monto inválido")
            return

        data = {
            "action": "create",
            "ticker": entry_ticker.get(),
            "fecha": entry_fecha.get(),
            "tipo": entry_tipo.get(),
            "monto": monto,
            "entrada": entry_entrada.get(),
            "target": entry_target.get(),
            "stop": entry_stop.get(),
            "nota_entrada": entry_nota_entrada.get(),
            "nota_salida": entry_nota_salida.get()
        }

        try:
            requests.post(URL, json=data, timeout=10)
            messagebox.showinfo("OK", "Guardado correctamente")
            limpiar()
            cargar_listado()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def editar_dato():
        id_sel = obtener_id_seleccionado()
        if not id_sel:
            messagebox.showerror("Error", "Selecciona un registro")
            return

        data = {
            "action": "update",
            "id": id_sel,
            "ticker": entry_ticker.get(),
            "fecha": entry_fecha.get(),
            "tipo": entry_tipo.get(),
            "monto": entry_monto.get(),
            "entrada": entry_entrada.get(),
            "target": entry_target.get(),
            "stop": entry_stop.get(),
            "nota_entrada": entry_nota_entrada.get(),
            "nota_salida": entry_nota_salida.get()
        }

        try:
            requests.post(URL, json=data)
            messagebox.showinfo("OK", "Actualizado")
            cargar_listado()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def borrar_dato():
        id_sel = obtener_id_seleccionado()
        if not id_sel:
            messagebox.showerror("Error", "Selecciona un registro")
            return

        try:
            requests.post(URL, json={"action": "delete", "id": id_sel})
            messagebox.showinfo("OK", "Eliminado")
            cargar_listado()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def limpiar():
        entry_ticker.delete(0, tk.END)
        entry_fecha.delete(0, tk.END)
        entry_tipo.delete(0, tk.END)
        entry_monto.delete(0, tk.END)
        entry_entrada.delete(0, tk.END)
        entry_target.delete(0, tk.END)
        entry_stop.delete(0, tk.END)
        entry_nota_entrada.delete(0, tk.END)
        entry_nota_salida.delete(0, tk.END)
        entry_fecha.insert(0, formatear_fecha())

    # ==============================
    # UI
    # ==============================

    ttk.Label(frame, text="Ticker").grid(row=0, column=0, sticky="w")
    entry_ticker = ttk.Entry(frame)
    entry_ticker.grid(row=0, column=1, sticky="ew")

    ttk.Label(frame, text="Fecha").grid(row=1, column=0, sticky="w")
    entry_fecha = ttk.Entry(frame)
    entry_fecha.grid(row=1, column=1, sticky="ew")
    entry_fecha.insert(0, formatear_fecha())

    ttk.Label(frame, text="Tipo").grid(row=2, column=0, sticky="w")
    entry_tipo = ttk.Entry(frame)
    entry_tipo.grid(row=2, column=1, sticky="ew")

    ttk.Label(frame, text="Monto").grid(row=3, column=0, sticky="w")
    entry_monto = ttk.Entry(frame)
    entry_monto.grid(row=3, column=1, sticky="ew")

    ttk.Label(frame, text="Entrada").grid(row=4, column=0, sticky="w")
    entry_entrada = ttk.Entry(frame)
    entry_entrada.grid(row=4, column=1, sticky="ew")

    ttk.Label(frame, text="Target").grid(row=5, column=0, sticky="w")
    entry_target = ttk.Entry(frame)
    entry_target.grid(row=5, column=1, sticky="ew")

    ttk.Label(frame, text="Stop Loss").grid(row=6, column=0, sticky="w")
    entry_stop = ttk.Entry(frame)
    entry_stop.grid(row=6, column=1, sticky="ew")

    ttk.Label(frame, text="Nota Entrada").grid(row=7, column=0, sticky="w")
    entry_nota_entrada = ttk.Entry(frame)
    entry_nota_entrada.grid(row=7, column=1, sticky="ew")

    ttk.Label(frame, text="Nota Salida").grid(row=8, column=0, sticky="w")
    entry_nota_salida = ttk.Entry(frame)
    entry_nota_salida.grid(row=8, column=1, sticky="ew")

    btn = ttk.Frame(frame)
    btn.grid(row=9, column=0, columnspan=2, pady=10)

    ttk.Button(btn, text="Guardar", command=enviar_datos).grid(row=0, column=0)
    ttk.Button(btn, text="Editar", command=editar_dato).grid(row=0, column=1)
    ttk.Button(btn, text="Borrar", command=borrar_dato).grid(row=0, column=2)
    ttk.Button(btn, text="Actualizar", command=cargar_listado).grid(row=0, column=3)

    columnas = (
        "ticker", "fecha", "tipo", "monto",
        "entrada", "target", "stop",
        "nota_entrada", "nota_salida"
    )

    tree_frame = ttk.Frame(frame)
    tree_frame.grid(row=10, column=0, columnspan=2, sticky="nsew")

    scroll_y = ttk.Scrollbar(tree_frame, orient="vertical")
    scroll_y.pack(side="right", fill="y")

    tree = ttk.Treeview(
        tree_frame,
        columns=columnas,
        show="headings",
        height=10,
        yscrollcommand=scroll_y.set
    )

    scroll_y.config(command=tree.yview)

    for c in columnas:
        tree.heading(c, text=c)
        tree.column(c, width=110)

    tree.pack(fill="both", expand=True)

    frame.rowconfigure(10, weight=1)
    frame.columnconfigure(1, weight=1)

    cargar_listado()

    return frame