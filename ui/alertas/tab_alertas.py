from tkinter import ttk, Toplevel, messagebox
from ui.alertas.funciones import URL

import requests

from ui.alertas.form_alertas import crear_formulario
from ui.alertas.tabla_alertas import crear_tabla
from ui.alertas.tabla_ejecucion import trades_eject
from ui.alertas.tabla_finalizados import trades_finish
from ui.alertas.funciones import (
    cargar_listado,
    cargar_ejecutados,
    cargar_finalizados,
    enviar_datos
)

# ==============================
# EDITAR (VENTANA NUEVA)
# ==============================
def abrir_editar(tree):

    sel = tree.selection()
    if not sel:
        messagebox.showerror("Error", "Selecciona un registro")
        return

    item = tree.item(sel[0])
    valores = item["values"]

    print("VALORES:", valores)

    if not valores:
        messagebox.showerror("Error", "Selecciona un registro válido")
        return

    # 👇 VALIDAR ID REAL (FIX CLAVE)
    try:
        id_real = int(valores[0])
    except:
        messagebox.showerror("Error", "Fila inválida (sin ID real)")
        return

    win = Toplevel()
    win.title("Editar")
    win.geometry("320x180")

    # ==============================
    # CAMPOS
    # ==============================
    ttk.Label(win, text="ID").grid(row=0, column=0, padx=10, pady=5, sticky="w")
    entry_id = ttk.Entry(win)
    entry_id.grid(row=0, column=1, padx=10, pady=5)
    entry_id.insert(0, valores[0])
    entry_id.config(state="disabled")

    ttk.Label(win, text="Ticker").grid(row=1, column=0, padx=10, pady=5, sticky="w")
    entry_ticker = ttk.Entry(win)
    entry_ticker.grid(row=1, column=1, padx=10, pady=5)
    entry_ticker.insert(0, valores[1])

    ttk.Label(win, text="Tipo").grid(row=2, column=0, padx=10, pady=5, sticky="w")
    entry_tipo = ttk.Entry(win)
    entry_tipo.grid(row=2, column=1, padx=10, pady=5)
    entry_tipo.insert(0, valores[2])

    # ==============================
    # BOTONES
    # ==============================
    def guardar():

        data = {
            "action": "update",
            "id": id_real,  # 👈 FIX
            "ticker": entry_ticker.get(),
            "tipo": entry_tipo.get(),
            "nota_entrada": ""
        }

        try:
            requests.post(URL, json=data)
            messagebox.showinfo("OK", "Actualizado")
            win.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def cancelar():
        win.destroy()

    ttk.Button(win, text="Guardar", command=guardar)\
        .grid(row=4, column=0, padx=10, pady=20)

    ttk.Button(win, text="Cancelar", command=cancelar)\
        .grid(row=4, column=1, padx=10, pady=20)


# ==============================
# BORRAR
# ==============================
def borrar_dato(tree):

    sel = tree.selection()
    if not sel:
        messagebox.showerror("Error", "Selecciona un registro")
        return

    item = tree.item(sel[0])
    valores = item["values"]

    if not valores:
        messagebox.showerror("Error", "Selecciona un registro válido")
        return

    # 👇 VALIDAR ID REAL (FIX CLAVE)
    try:
        id_sel = int(valores[0])
    except:
        messagebox.showerror("Error", "Fila inválida (sin ID real)")
        return

    try:
        requests.post(URL, json={"action": "delete", "id": id_sel})
        messagebox.showinfo("OK", "Eliminado")
    except Exception as e:
        messagebox.showerror("Error", str(e))


# ==============================
# MAIN TAB
# ==============================
def crear_tab_alertas(parent):

    frame = ttk.Frame(parent, padding=10)

    # ==============================
    # FORM
    # ==============================
    form_entries, last_row = crear_formulario(frame)

    # ==============================
    # BOTONES
    # ==============================
    btn = ttk.Frame(frame)
    btn.grid(row=last_row, column=0, columnspan=2, pady=10)

    # ==============================
    # NOTEBOOK
    # ==============================
    notebook = ttk.Notebook(frame)
    notebook.grid(row=last_row + 1, column=0, columnspan=2, sticky="nsew")

    # ==============================
    # TAB 1: ALERTAS
    # ==============================
    frame_tabla = ttk.Frame(notebook)
    notebook.add(frame_tabla, text="Alertas")

    frame_tabla.rowconfigure(0, weight=1)
    frame_tabla.columnconfigure(0, weight=1)

    tree_alertas = crear_tabla(frame_tabla, 0)

    # ==============================
    # TAB 2: EJECUCIÓN
    # ==============================
    frame_ejecucion = ttk.Frame(notebook)
    notebook.add(frame_ejecucion, text="Trades en Ejecución")

    frame_ejecucion.rowconfigure(0, weight=1)
    frame_ejecucion.columnconfigure(0, weight=1)

    tree_ejecucion = trades_eject(frame_ejecucion, 0)

    # ==============================
    # TAB 3: FINALIZADOS
    # ==============================
    frame_finalizados = ttk.Frame(notebook)
    notebook.add(frame_finalizados, text="Trades Finalizados")

    frame_finalizados.rowconfigure(0, weight=1)
    frame_finalizados.columnconfigure(0, weight=1)

    tree_finalizados = trades_finish(frame_finalizados, 0)

    # ==============================
    # GRID
    # ==============================
    frame.rowconfigure(last_row + 1, weight=1)
    frame.columnconfigure(1, weight=1)

    # ==============================
    # CARGA INICIAL
    # ==============================
    cargar_listado(tree_alertas)
    cargar_ejecutados(tree_ejecucion)
    cargar_finalizados(tree_finalizados)

    # ==============================
    # BOTONES
    # ==============================
    ttk.Button(btn, text="Guardar",
               command=lambda: enviar_datos(form_entries, tree_alertas)).grid(row=0, column=0)

    ttk.Button(btn, text="Editar",
               command=lambda: abrir_editar(tree_alertas)).grid(row=0, column=1)

    ttk.Button(btn, text="Borrar",
               command=lambda: borrar_dato(tree_alertas)).grid(row=0, column=2)

    ttk.Button(btn, text="Actualizar",
               command=lambda: (
                   cargar_listado(tree_alertas),
                   cargar_ejecutados(tree_ejecucion),
                   cargar_finalizados(tree_finalizados)
               )).grid(row=0, column=3)

    return frame