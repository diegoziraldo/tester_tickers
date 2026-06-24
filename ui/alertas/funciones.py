import requests
from tkinter import messagebox
from datetime import datetime
import os
import sys

# ==============================
# CONFIG
# ==============================

def obtener_ruta_config():
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, "../../datos.txt")


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

# ==============================
# HELPERS
# ==============================

def normalizar_fecha(fecha):
    try:
        return datetime.fromisoformat(fecha).strftime("%d/%m/%Y")
    except:
        return fecha


def obtener_id_seleccionado(tree):
    sel = tree.selection()
    if not sel:
        return None
    return sel[0]   # 👈 ID real guardado en iid

# ==============================
# CRUD
# ==============================

def cargar_listado(tree):
    try:
        r = requests.post(URL, json={"action": "read_para_app"}, timeout=10)
        data = r.json()

        for item in tree.get_children():
            tree.delete(item)

        for row in data:
            tree.insert(
                "",
                "end",
                iid=row.get("id"),  # 👈 ID REAL
                values=(
                    row.get("ticker"),
                    row.get("tipo"),
                    row.get("nota_entrada")
                )
            )

    except Exception as e:
        messagebox.showerror("Error", str(e))


def cargar_ejecutados(tree):
    try:
        r = requests.post(URL, json={"action": "read_para_app"}, timeout=10)
        data = r.json()

        for item in tree.get_children():
            tree.delete(item)

        for row in data:
            tree.insert("", "end", values=(
                row.get("id"),
                row.get("ticker"),
                normalizar_fecha(row.get("fecha")),
                row.get("tipo"),
                row.get("monto"),
                row.get("entrada"),
                row.get("fecha_salida"),
                row.get("target"),
                row.get("stop"),
                row.get("estado"),
                row.get("nota_entrada"),
                row.get("nota_salida")
            ))

    except Exception as e:
        messagebox.showerror("Error", str(e))


def cargar_finalizados(tree):
    try:
        r = requests.post(URL, json={"action": "read_para_app"}, timeout=10)
        data = r.json()

        for item in tree.get_children():
            tree.delete(item)

        for row in data:
            tree.insert("", "end", values=(
                row.get("id"),
                row.get("ticker"),
                normalizar_fecha(row.get("fecha")),
                row.get("tipo"),
                row.get("monto"),
                row.get("entrada"),
                row.get("fecha_salida"),
                row.get("target"),
                row.get("stop"),
                row.get("estado"),
                row.get("nota_entrada"),
                row.get("nota_salida")
            ))

    except Exception as e:
        messagebox.showerror("Error", str(e))


# ==============================
# CREATE
# ==============================

def enviar_datos(entries, tree):

    try:
        monto = entries["monto"].get()
        monto = float(monto) if monto else None
    except:
        messagebox.showerror("Error", "Monto inválido")
        return

    data = {
        "action": "create",
        "fecha": entries["fecha"].get(),
        "fecha_salida": entries.get("fecha_salida", "").get() if "fecha_salida" in entries else "",
        "ticker": entries["ticker"].get(),
        "tipo": entries["tipo"].get(),
        "monto": monto,
        "entrada": entries["entrada"].get(),
        "target": entries["target"].get(),
        "stop": entries["stop"].get(),
        "estado": entries["estado"].get(),
        "nota_entrada": entries["nota_entrada"].get(),
        "nota_salida": entries["nota_salida"].get()
    }

    try:
        requests.post(URL, json=data)
        messagebox.showinfo("OK", "Guardado correctamente")
        cargar_listado(tree)
    except Exception as e:
        messagebox.showerror("Error", str(e))


# ==============================
# UPDATE
# ==============================

def editar_dato(entries, tree):

    id_sel = obtener_id_seleccionado(tree)
    if not id_sel:
        messagebox.showerror("Error", "Selecciona un registro")
        return

    data = {
        "action": "update",
        "id": id_sel,
        "fecha": entries["fecha"].get(),
        "fecha_salida": entries.get("fecha_salida", "").get() if "fecha_salida" in entries else "",
        "ticker": entries["ticker"].get(),
        "tipo": entries["tipo"].get(),
        "monto": entries["monto"].get(),
        "entrada": entries["entrada"].get(),
        "target": entries["target"].get(),
        "stop": entries["stop"].get(),
        "estado": entries["estado"].get(),
        "nota_entrada": entries["nota_entrada"].get(),
        "nota_salida": entries["nota_salida"].get()
    }

    try:
        requests.post(URL, json=data)
        messagebox.showinfo("OK", "Actualizado")
        cargar_listado(tree)
    except Exception as e:
        messagebox.showerror("Error", str(e))


# ==============================
# DELETE
# ==============================

def borrar_dato(tree):

    id_sel = obtener_id_seleccionado(tree)
    if not id_sel:
        messagebox.showerror("Error", "Selecciona un registro")
        return

    try:
        requests.post(URL, json={"action": "delete", "id": id_sel})
        messagebox.showinfo("OK", "Eliminado")
        cargar_listado(tree)
    except Exception as e:
        messagebox.showerror("Error", str(e))