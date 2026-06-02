"""
graph.py – Funciones de visualización con Plotly.
"""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def grafico_distribucion_notas(df):
    fig = px.histogram(df, x="Final_Exam_Score", nbins=40, color="Gender",
        barmode="overlay", opacity=0.75,
        color_discrete_sequence=px.colors.qualitative.Set2,
        labels={"Final_Exam_Score": "Nota Final", "count": "Estudiantes"})
    fig.update_layout(legend_title_text="Género", margin=dict(t=20, b=20))
    return fig

def grafico_riesgo_por_carrera(df):
    data = (df.groupby("Major_Subject")["Alerta_Riesgo"]
        .mean().mul(100).reset_index()
        .rename(columns={"Alerta_Riesgo": "Pct_Riesgo"})
        .sort_values("Pct_Riesgo", ascending=True))
    fig = px.bar(data, x="Pct_Riesgo", y="Major_Subject", orientation="h",
        color="Pct_Riesgo", color_continuous_scale="RdYlGn_r",
        labels={"Pct_Riesgo": "% En riesgo", "Major_Subject": "Carrera"})
    fig.update_layout(coloraxis_showscale=False, margin=dict(t=20, b=20))
    return fig

def grafico_estudio_vs_nota(df):
    sample = df.sample(min(3000, len(df)), random_state=42).copy()
    sample["Estado"] = sample["Alerta_Riesgo"].map({True: "En riesgo", False: "Sin riesgo"})
    fig = px.scatter(sample, x="Weekly_Study_Hours", y="Final_Exam_Score",
        color="Estado",
        color_discrete_map={"En riesgo": "#EF553B", "Sin riesgo": "#00CC96"},
        category_orders={"Estado": ["Sin riesgo", "En riesgo"]},
        opacity=0.5, trendline="ols",
        labels={"Weekly_Study_Hours": "Horas semanales de estudio",
                "Final_Exam_Score": "Nota Final", "Estado": "Estado del alumno"})
    fig.update_layout(legend_title_text="Estado del alumno", margin=dict(t=20, b=20))
    return fig

def grafico_evolucion_semestre(df):
    ev = (df.groupby("Semester_ID")[["Final_Exam_Score","Midterm_Mark","Previous_GPA"]]
          .mean().reset_index())
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=ev["Semester_ID"], y=ev["Final_Exam_Score"],
        mode="lines+markers", name="Nota Final", yaxis="y1"))
    fig.add_trace(go.Scatter(x=ev["Semester_ID"], y=ev["Midterm_Mark"],
        mode="lines+markers", name="Parcial", yaxis="y1"))
    fig.add_trace(go.Scatter(x=ev["Semester_ID"], y=ev["Previous_GPA"],
        mode="lines+markers", name="GPA promedio", line=dict(dash="dot"), yaxis="y2"))
    fig.update_layout(
        xaxis_title="Semestre",
        yaxis=dict(title="Nota (0–100)", side="left"),
        yaxis2=dict(title="GPA (0–4)", side="right", overlaying="y", showgrid=False),
        legend_title_text="Métrica",
        margin=dict(t=20, b=20),
    )
    return fig

def grafico_estres_sueno(df):
    fig = px.density_heatmap(df, x="Sleep_Hours", y="Stress_Level",
        nbinsx=20, nbinsy=20, color_continuous_scale="Viridis",
        labels={"Sleep_Hours": "Horas de sueño", "Stress_Level": "Nivel de estrés"})
    fig.update_layout(margin=dict(t=20, b=20))
    return fig

def grafico_top_universidades(df):
    top = (df.groupby("University_Name")["Final_Exam_Score"]
        .agg(["mean","count"]).query("count >= 50")
        .nlargest(10,"mean").reset_index()
        .rename(columns={"mean":"Promedio","count":"N"})
        .sort_values("Promedio"))
    fig = px.bar(top, x="Promedio", y="University_Name", orientation="h",
        color="Promedio", color_continuous_scale="Blues", hover_data=["N"],
        labels={"University_Name": "Universidad", "N": "Estudiantes"})
    fig.update_layout(coloraxis_showscale=False, margin=dict(t=20, b=20))
    return fig
