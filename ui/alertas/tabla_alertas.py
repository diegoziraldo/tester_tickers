from tkinter import ttk

def crear_tabla(frame):

    columnas = (
        "ticker", "fechaEntrada","fechaSalida", "tipo", "monto",
        "entrada", "target", "stop", "estado",
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

    return tree