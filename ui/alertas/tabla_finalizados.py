from tkinter import ttk

def trades_finish(frame, row):

    columnas = (
        "Ticker", "Fecha de entrada", "Fecha de salida", "Tipo",
        "Entrada", "Stop loss", "Target", "Ganador",
        "Nota entrada", "Nota salida"
    )

    tree_frame = ttk.Frame(frame)
    tree_frame.grid(row=row, column=0, columnspan=2, sticky="nsew")

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