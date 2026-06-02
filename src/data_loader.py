"""
data_loader.py – Carga y cacheo del dataset limpio.
"""

import os
import pandas as pd
import streamlit as st


@st.cache_data
def cargar_datos() -> pd.DataFrame:
    """Lee dataset_CLEAN.csv desde la carpeta data/ del proyecto."""
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ruta = os.path.join(base, "data", "dataset_CLEAN.csv")
    df = pd.read_csv(ruta)
    df["Alerta_Riesgo"] = df["Alerta_Riesgo"].astype(bool)
    return df
