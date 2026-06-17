"""
data_loader.py – Carga y cacheo del dataset limpio.
"""

import os
import pandas as pd
import streamlit as st


@st.cache_data
def cargar_datos() -> pd.DataFrame:
    """Lee dataset_CLEAN.csv desde la carpeta data/ del proyecto.

    Maneja con try-except los errores típicos (archivo ausente, CSV vacío o
    corrupto) y detiene la app con un mensaje claro para el usuario final.
    """
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ruta = os.path.join(base, "data", "dataset_CLEAN.csv")
    try:
        df = pd.read_csv(ruta)
        df["Alerta_Riesgo"] = df["Alerta_Riesgo"].astype(bool)
        return df
    except FileNotFoundError:
        st.error(
            "❌ No se encontró `data/dataset_CLEAN.csv`. "
            "Descargá el dataset desde el Drive/Release del repo (ver README) "
            "o ejecutá el ETL del Hito 2."
        )
        st.stop()
    except (pd.errors.EmptyDataError, pd.errors.ParserError):
        st.error("❌ El archivo `dataset_CLEAN.csv` está vacío o dañado. Volvé a generarlo con el ETL.")
        st.stop()
    except KeyError:
        st.error("❌ El dataset no tiene la columna `Alerta_Riesgo`. Regenerá el CSV con el feature engineering del Hito 2.")
        st.stop()
