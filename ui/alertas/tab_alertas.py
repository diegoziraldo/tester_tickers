from tkinter import ttk

from ui.alertas.form_alertas import crear_formulario
from ui.alertas.tabla_alertas import crear_tabla
from ui.alertas.tabla_ejecucion import trades_eject
from ui.alertas.tabla_finalizados import trades_finish
from ui.alertas.funciones import (
    cargar_listado,
    cargar_ejecutados,
    cargar_finalizados,
    enviar_datos,
    editar_dato,
    borrar_dato
)


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
    # NOTEBOOK (TABLAS)
    # ==============================
    notebook = ttk.Notebook(frame)
    notebook.grid(row=last_row + 1, column=0, columnspan=2, sticky="nsew")

    # =====================================================
    # 🔴 TAB 1: ALERTAS
    # =====================================================
    frame_tabla = ttk.Frame(notebook)
    notebook.add(frame_tabla, text="Alertas")

    frame_tabla.rowconfigure(0, weight=1)
    frame_tabla.columnconfigure(0, weight=1)

    tree_alertas = crear_tabla(frame_tabla, 0)

    # =====================================================
    # 🟡 TAB 2: TRADES EN EJECUCIÓN
    # =====================================================
    frame_ejecucion = ttk.Frame(notebook)
    notebook.add(frame_ejecucion, text="Trades en Ejecución")

    frame_ejecucion.rowconfigure(0, weight=1)
    frame_ejecucion.columnconfigure(0, weight=1)

    tree_ejecucion = trades_eject(frame_ejecucion, 0)


    # =====================================================
    # 🟡 TAB 2: TRADES EN EJECUCIÓN
    # =====================================================
    frame_finalizados = ttk.Frame(notebook)
    notebook.add(frame_finalizados, text="Trades Finalizados")

    frame_finalizados.rowconfigure(0, weight=1)
    frame_finalizados.columnconfigure(0, weight=1)

    tree_finalizados = trades_finish(frame_finalizados, 0)







    # ==============================
    # CONFIG GRID
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
    # BOTONES (trabajan sobre alertas)
    # ==============================
    ttk.Button(btn, text="Guardar",
               command=lambda: enviar_datos(form_entries, tree_alertas)).grid(row=0, column=0)

    ttk.Button(btn, text="Editar",
               command=lambda: editar_dato(form_entries, tree_alertas)).grid(row=0, column=1)

    ttk.Button(btn, text="Borrar",
               command=lambda: borrar_dato(tree_alertas)).grid(row=0, column=2)

    ttk.Button(btn, text="Actualizar",
            command=lambda: (cargar_listado(tree_alertas), 
                            cargar_ejecutados(tree_ejecucion), 
                            cargar_finalizados(tree_finalizados))
                            ).grid(row=0, column=3),


    return frame