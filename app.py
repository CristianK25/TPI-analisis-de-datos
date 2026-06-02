"""
app.py – Hito 4: Dashboard Interactivo
Orquesta carga de datos, filtros, KPIs y gráficos.
"""

import sys
import os

# Permite importar módulos desde src/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

import streamlit as st

from data_loader import cargar_datos
from filters import aplicar_filtros
from kpis import mostrar_kpis
from graph import (
    grafico_distribucion_notas,
    grafico_riesgo_por_carrera,
    grafico_estudio_vs_nota,
    grafico_evolucion_semestre,
    grafico_estres_sueno,
    grafico_top_universidades,
)

# ── Configuración ──────────────────────────────
st.set_page_config(
    page_title="Dashboard Académico",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Datos ──────────────────────────────────────
df_full = cargar_datos()
df = aplicar_filtros(df_full)

# ── Encabezado ─────────────────────────────────
st.title("🎓 Dashboard Académico – Análisis de Rendimiento Estudiantil")
st.caption(f"Mostrando **{len(df):,}** estudiantes de {len(df_full):,} totales")

if df.empty:
    st.warning("No hay datos para los filtros seleccionados.")
    st.stop()

# ── Alerta automática de riesgo ────────────────
pct_riesgo = df["Alerta_Riesgo"].mean() * 100
if pct_riesgo >= 20:
    st.error(f"🚨 **Atención:** el {pct_riesgo:.1f}% de los alumnos seleccionados está en riesgo (baja asistencia + bajo GPA). Se recomienda intervención.")
elif pct_riesgo >= 10:
    st.warning(f"⚠️ El {pct_riesgo:.1f}% de los alumnos seleccionados presenta indicadores de riesgo académico.")

# ── KPIs ───────────────────────────────────────
mostrar_kpis(df, total=len(df_full))
st.divider()

# ── Fila 1 ─────────────────────────────────────
c1, c2 = st.columns(2)
with c1:
    st.subheader("Distribución de notas finales")
    st.caption("Cómo se distribuyen las notas del examen final según género. El pico más a la derecha indica mejor rendimiento.")
    st.plotly_chart(grafico_distribucion_notas(df), use_container_width=True)
with c2:
    st.subheader("% Alumnos en riesgo por carrera")
    st.caption("Porcentaje de alumnos con baja asistencia Y bajo GPA simultáneamente. Rojo = mayor urgencia de intervención.")
    st.plotly_chart(grafico_riesgo_por_carrera(df), use_container_width=True)

# ── Fila 2 ─────────────────────────────────────
c3, c4 = st.columns(2)
with c3:
    st.subheader("Horas de estudio vs. Nota final")
    st.caption("Cada punto es un alumno. Los rojos están en riesgo. La línea muestra la tendencia general: más horas de estudio, mejor nota.")
    st.plotly_chart(grafico_estudio_vs_nota(df), use_container_width=True)
with c4:
    st.subheader("Rendimiento promedio por semestre")
    st.caption("Evolución de notas (escala izquierda) y GPA promedio (escala derecha) a lo largo de los semestres.")
    st.plotly_chart(grafico_evolucion_semestre(df), use_container_width=True)

# ── Fila 3 ─────────────────────────────────────
c5, c6 = st.columns(2)
with c5:
    st.subheader("Estrés vs. Horas de sueño")
    st.caption("Las zonas más oscuras concentran más alumnos. Zonas de alto estrés y poco sueño son señales de riesgo de agotamiento.")
    st.plotly_chart(grafico_estres_sueno(df), use_container_width=True)
with c6:
    st.subheader("Top 10 universidades por nota media")
    st.caption("Solo universidades con al menos 50 alumnos en la selección actual. Pasá el cursor sobre las barras para ver la cantidad.")
    st.plotly_chart(grafico_top_universidades(df), use_container_width=True)

# ── Tabla expandible ───────────────────────────
with st.expander("📋 Ver tabla de datos filtrados (primeros 500)"):
    cols = [
        "Student_ID", "Semester_ID", "Age", "Gender", "Major_Subject",
        "Attendance_Rate", "Previous_GPA", "Final_Exam_Score",
        "Eficiencia_Estudio", "Alerta_Riesgo",
    ]
    st.dataframe(df[cols].head(500), use_container_width=True)

st.caption("Dashboard generado con Streamlit + Plotly · Hito 4 TPI")
