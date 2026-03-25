import pandas as pd
import requests
import io
from config import URL_ESTRATEGIAS, estrategias

def cargar_estrategias_desde_sheets(estrategia_select, root, cargar_estrategia):
    try:
        resp = requests.get(URL_ESTRATEGIAS)
        resp.raise_for_status()

        df = pd.read_csv(io.StringIO(resp.text))

        estrategias.clear()

        for _, row in df.iterrows():
            nombre = row["nombre"]
            config = {}

            for col in df.columns:
                if col.lower() == "nombre":
                    continue

                val = row[col]

                if pd.isna(val):
                    continue

                try:
                    config[col.upper()] = float(val)
                except:
                    pass

            estrategias[nombre] = config

        valores = list(estrategias.keys())
        estrategia_select["values"] = valores

        actual = estrategia_select.get()

        estrategia_select.set("")
        root.update_idletasks()

        if actual in valores:
            estrategia_select.set(actual)
            cargar_estrategia()

    except Exception as e:
        print("Error cargando estrategias:", e)