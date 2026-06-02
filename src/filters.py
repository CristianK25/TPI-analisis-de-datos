"""
filters.py – Sidebar con filtros interactivos.
Devuelve el DataFrame filtrado y los valores seleccionados.
"""

import pandas as pd
import streamlit as st


def aplicar_filtros(df: pd.DataFrame) -> pd.DataFrame:
    """Renderiza el sidebar y devuelve el DataFrame filtrado."""
    st.sidebar.title("🔍 Filtros")

    # Comisión / Semestre
    semestres = sorted(df["Semester_ID"].unique())
    sel_semestres = st.sidebar.multiselect(
        "Comisión (Semestre)",
        options=semestres,
        default=semestres,
        format_func=lambda x: f"Semestre {x}",
    )

    # Estado de alerta
    estado_opciones = {"Todos": None, "En Riesgo ⚠️": True, "Sin Riesgo ✅": False}
    sel_estado = st.sidebar.radio("Estado de alerta", list(estado_opciones.keys()))

    # Género
    generos = sorted(df["Gender"].unique())
    sel_generos = st.sidebar.multiselect("Género", options=generos, default=generos)

    # Carrera
    carreras = sorted(df["Major_Subject"].unique())
    sel_carreras = st.sidebar.multiselect("Carrera", options=carreras, default=carreras)

    # Rango de edad
    edad_min, edad_max = int(df["Age"].min()), int(df["Age"].max())
    sel_edad = st.sidebar.slider("Rango de edad", edad_min, edad_max, (edad_min, edad_max))

    # ── Aplicar filtros ──
    mask = (
        df["Semester_ID"].isin(sel_semestres) &
        df["Gender"].isin(sel_generos) &
        df["Major_Subject"].isin(sel_carreras) &
        df["Age"].between(sel_edad[0], sel_edad[1])
    )
    df_filtrado = df[mask]

    estado_val = estado_opciones[sel_estado]
    if estado_val is not None:
        df_filtrado = df_filtrado[df_filtrado["Alerta_Riesgo"] == estado_val]

    return df_filtrado
