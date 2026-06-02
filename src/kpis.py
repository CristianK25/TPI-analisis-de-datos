"""
kpis.py – Métricas resumen (fila de KPIs) del dashboard.
"""

import pandas as pd
import streamlit as st


def mostrar_kpis(df: pd.DataFrame, total: int) -> None:
    """Renderiza 5 métricas clave en la parte superior del dashboard."""
    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("Estudiantes", f"{len(df):,}")
    col2.metric("Promedio Final", f"{df['Final_Exam_Score'].mean():.1f}")
    col3.metric("Promedio GPA", f"{df['Previous_GPA'].mean():.2f}")
    col4.metric("Asistencia media", f"{df['Attendance_Rate'].mean():.1f}%")
    col5.metric(
        "En riesgo",
        f"{df['Alerta_Riesgo'].sum():,}",
        delta=f"{df['Alerta_Riesgo'].mean() * 100:.1f}%",
        delta_color="inverse",
    )
