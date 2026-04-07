import tkinter as tk
from tkinter import ttk
from datetime import datetime

def formatear_fecha():
    return datetime.now().strftime("%d/%m/%Y")

def crear_formulario(frame):

    entries = {}

    campos = [
        "ticker", "fecha", "tipo", "monto",
        "entrada", "target", "stop", "estado",
        "nota_entrada", "nota_salida"
    ]

    for i, campo in enumerate(campos):
        ttk.Label(frame, text=campo.capitalize()).grid(row=i, column=0, sticky="w")

        entry = ttk.Entry(frame)
        entry.grid(row=i, column=1, sticky="ew")

        entries[campo] = entry

    entries["fecha"].insert(0, formatear_fecha())

    return entries