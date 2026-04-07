from tkinter import ttk

from ui.alertas.form_alertas import crear_formulario
from ui.alertas.tabla_alertas import crear_tabla
from ui.alertas.funciones import (
    cargar_listado,
    enviar_datos,
    editar_dato,
    borrar_dato
)

def crear_tab_alertas(parent):

    frame = ttk.Frame(parent, padding=15)

    # FORM
    form_entries = crear_formulario(frame)

    # TABLA
    tree = crear_tabla(frame)

    # BOTONES
    btn = ttk.Frame(frame)
    btn.grid(row=9, column=0, columnspan=2, pady=10)

    ttk.Button(btn, text="Guardar",
               command=lambda: enviar_datos(form_entries, tree)).grid(row=0, column=0)

    ttk.Button(btn, text="Editar",
               command=lambda: editar_dato(form_entries, tree)).grid(row=0, column=1)

    ttk.Button(btn, text="Borrar",
               command=lambda: borrar_dato(tree)).grid(row=0, column=2)

    ttk.Button(btn, text="Actualizar",
               command=lambda: cargar_listado(tree)).grid(row=0, column=3)

    # CONFIG GRID
    frame.rowconfigure(10, weight=1)
    frame.columnconfigure(1, weight=1)

    cargar_listado(tree)

    return frame