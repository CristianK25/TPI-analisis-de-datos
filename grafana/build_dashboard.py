"""
build_dashboard.py – Genera el dashboard.json de Grafana del Hito 3.

Se mantiene el dashboard como código para que sea reproducible y revisable.
Genera dos copias idénticas:
  - grafana/dashboards/tpi_dashboard.json  (lo provisiona Grafana al arrancar)
  - dashboard.json                          (entrega final en la raíz del repo)
"""

import json
import os

DS = {"type": "postgres", "uid": "tpi_postgres"}
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def target(sql):
    return [{
        "datasource": DS,
        "format": "table",
        "rawQuery": True,
        "rawSql": sql,
        "refId": "A",
    }]


def stat_panel(pid, title, sql, x, unit="", color="blue", decimals=1):
    return {
        "id": pid,
        "type": "stat",
        "title": title,
        "datasource": DS,
        "gridPos": {"h": 4, "w": 6, "x": x, "y": 0},
        "targets": target(sql),
        "fieldConfig": {
            "defaults": {
                "unit": unit,
                "decimals": decimals,
                "color": {"mode": "fixed", "fixedColor": color},
            },
            "overrides": [],
        },
        "options": {
            "colorMode": "background",
            "graphMode": "none",
            "justifyMode": "center",
            "reduceOptions": {"calcs": ["lastNotNull"], "fields": "", "values": False},
            "textMode": "value_and_name",
        },
    }


def line_panel(pid, title, desc, sql, x, y, w, h, xfield, ymin, ymax, ytitle, palette):
    """Panel de líneas (trend) con eje X numérico = horas de estudio.

    Importante: min/max/axisLabel se aplican SOLO a las series del eje Y
    (vía overrides byName); si se pusieran en defaults afectarían también al
    eje X (horas de estudio) y romperían su escala.
    """
    overrides = []
    for name, col in palette.items():
        overrides.append({
            "matcher": {"id": "byName", "options": name},
            "properties": [
                {"id": "color", "value": {"mode": "fixed", "fixedColor": col}},
                {"id": "min", "value": ymin},
                {"id": "max", "value": ymax},
                {"id": "custom.axisLabel", "value": ytitle},
                {"id": "custom.axisPlacement", "value": "left"},
            ],
        })
    # El campo del eje X no debe dibujarse como serie ni llevar escala Y.
    overrides.append({
        "matcher": {"id": "byName", "options": xfield},
        "properties": [{"id": "custom.axisLabel", "value": "Horas de estudio (semanales)"}],
    })
    return {
        "id": pid,
        "type": "trend",
        "title": title,
        "description": desc,
        "datasource": DS,
        "gridPos": {"h": h, "w": w, "x": x, "y": y},
        "targets": target(sql),
        "options": {
            "xField": xfield,
            "legend": {"displayMode": "list", "placement": "bottom", "showLegend": True},
            "tooltip": {"mode": "multi", "sort": "none"},
        },
        "fieldConfig": {
            "defaults": {
                "custom": {
                    "drawStyle": "line",
                    "lineInterpolation": "linear",
                    "lineWidth": 3,
                    "pointSize": 5,
                    "showPoints": "never",
                    "fillOpacity": 10,
                    "spanNulls": True,
                },
                "unit": "none",
                "decimals": 1,
            },
            "overrides": overrides,
        },
    }


def bar_panel(pid, title, desc, sql, x, y, w, h, orientation, palette,
              xfield, unit="none", ymin=None, ymax=None, ytitle=""):
    overrides = []
    for name, col in palette.items():
        overrides.append({
            "matcher": {"id": "byName", "options": name},
            "properties": [{"id": "color", "value": {"mode": "fixed", "fixedColor": col}}],
        })
    defaults = {
        "custom": {
            "lineWidth": 1,
            "fillOpacity": 85,
            "axisLabel": ytitle,
            "gradientMode": "none",
        },
        "unit": unit,
        "decimals": 1,
    }
    if ymin is not None:
        defaults["min"] = ymin
    if ymax is not None:
        defaults["max"] = ymax
    return {
        "id": pid,
        "type": "barchart",
        "title": title,
        "description": desc,
        "datasource": DS,
        "gridPos": {"h": h, "w": w, "x": x, "y": y},
        "targets": target(sql),
        "options": {
            "orientation": orientation,
            "xField": xfield,
            "showValue": "auto",
            "stacking": "none",
            "groupWidth": 0.7,
            "barWidth": 0.9,
            "legend": {"displayMode": "list", "placement": "bottom", "showLegend": True},
            "tooltip": {"mode": "multi", "sort": "none"},
        },
        "fieldConfig": {"defaults": defaults, "overrides": overrides},
    }


# --------------------------------------------------------------------------- #
# Consultas SQL
# --------------------------------------------------------------------------- #

SQL_KPI_TOTAL = 'SELECT count(*) AS "Estudiantes" FROM students;'
SQL_KPI_NOTA = 'SELECT round(avg(final_exam_score)::numeric, 1) AS "Nota Final" FROM students;'
SQL_KPI_ASIST = 'SELECT round(avg(attendance_rate)::numeric, 1) AS "Asistencia" FROM students;'
SQL_KPI_RIESGO = 'SELECT round(100.0 * avg(alerta_riesgo::int)::numeric, 1) AS "% En Riesgo" FROM students;'

# P1 – Agotamiento: líneas de tendencia OLS (misma metodología que el notebook)
# de la nota final vs. horas de estudio, según agotamiento (estrés >=7 + sueño <6)
# vs. resto. Se usa regr_slope/regr_intercept para evitar que los outliers del
# perfil "Ansiedad" (analizado en P3, concentrado >30h) deformen la tendencia.
SQL_P1 = """
WITH coef AS (
  SELECT
    regr_slope(final_exam_score, weekly_study_hours)
      FILTER (WHERE stress_level >= 7 AND sleep_hours < 6) AS s_ag,
    regr_intercept(final_exam_score, weekly_study_hours)
      FILTER (WHERE stress_level >= 7 AND sleep_hours < 6) AS i_ag,
    regr_slope(final_exam_score, weekly_study_hours)
      FILTER (WHERE NOT (stress_level >= 7 AND sleep_hours < 6)) AS s_de,
    regr_intercept(final_exam_score, weekly_study_hours)
      FILTER (WHERE NOT (stress_level >= 7 AND sleep_hours < 6)) AS i_de
  FROM students
)
SELECT
  g.x AS "Horas de estudio (semanales)",
  round((coef.i_ag + coef.s_ag * g.x)::numeric, 1) AS "Agotado (estrés alto + poco sueño)",
  round((coef.i_de + coef.s_de * g.x)::numeric, 1) AS "Descansado (resto)"
FROM coef, generate_series(0, 40, 2) AS g(x)
ORDER BY g.x;
""".strip()

# P2 – Brecha digital: líneas de tendencia OLS de la nota final vs. horas de
# estudio, según calidad de la conexión a internet.
SQL_P2 = """
WITH coef AS (
  SELECT
    regr_slope(final_exam_score, weekly_study_hours)
      FILTER (WHERE internet_quality < 4.5) AS s_m,
    regr_intercept(final_exam_score, weekly_study_hours)
      FILTER (WHERE internet_quality < 4.5) AS i_m,
    regr_slope(final_exam_score, weekly_study_hours)
      FILTER (WHERE internet_quality >= 4.5 AND internet_quality < 7.5) AS s_r,
    regr_intercept(final_exam_score, weekly_study_hours)
      FILTER (WHERE internet_quality >= 4.5 AND internet_quality < 7.5) AS i_r,
    regr_slope(final_exam_score, weekly_study_hours)
      FILTER (WHERE internet_quality >= 7.5) AS s_e,
    regr_intercept(final_exam_score, weekly_study_hours)
      FILTER (WHERE internet_quality >= 7.5) AS i_e
  FROM students
)
SELECT
  g.x AS "Horas de estudio (semanales)",
  round((coef.i_m + coef.s_m * g.x)::numeric, 1) AS "Internet Malo / Crítico (0-4.5)",
  round((coef.i_r + coef.s_r * g.x)::numeric, 1) AS "Internet Regular / Bueno (4.6-7.5)",
  round((coef.i_e + coef.s_e * g.x)::numeric, 1) AS "Internet Excelente (7.6-10)"
FROM coef, generate_series(0, 40, 2) AS g(x)
ORDER BY g.x;
""".strip()

# P3 – Comportamientos atípicos: hábitos del perfil "Autónomo Exitoso"
# (asistencia <60% y nota >=80) vs "Ansiedad / Esfuerzo Ineficiente"
# (horas >=30 y nota <60).
SQL_P3 = """
SELECT 'Visitas Biblioteca / mes' AS "Hábito",
  round(avg(library_visits_per_month) FILTER (
        WHERE attendance_rate < 60 AND final_exam_score >= 80)::numeric, 2)
        AS "Autónomo Exitoso",
  round(avg(library_visits_per_month) FILTER (
        WHERE weekly_study_hours >= 30 AND final_exam_score < 60)::numeric, 2)
        AS "Ansiedad / Esfuerzo Ineficiente"
FROM students
UNION ALL
SELECT 'Motivación (1-10)',
  round(avg(motivation_score) FILTER (WHERE attendance_rate < 60 AND final_exam_score >= 80)::numeric, 2),
  round(avg(motivation_score) FILTER (WHERE weekly_study_hours >= 30 AND final_exam_score < 60)::numeric, 2)
FROM students
UNION ALL
SELECT 'Autoeficacia (1-10)',
  round(avg(self_efficacy_score) FILTER (WHERE attendance_rate < 60 AND final_exam_score >= 80)::numeric, 2),
  round(avg(self_efficacy_score) FILTER (WHERE weekly_study_hours >= 30 AND final_exam_score < 60)::numeric, 2)
FROM students
UNION ALL
SELECT 'Nivel de Estrés (1-10)',
  round(avg(stress_level) FILTER (WHERE attendance_rate < 60 AND final_exam_score >= 80)::numeric, 2),
  round(avg(stress_level) FILTER (WHERE weekly_study_hours >= 30 AND final_exam_score < 60)::numeric, 2)
FROM students;
""".strip()

# Bonus – % de alumnos en riesgo por carrera.
SQL_CARRERA = """
SELECT
  major_subject AS "Carrera",
  round(100.0 * avg(alerta_riesgo::int)::numeric, 1) AS "% En Riesgo"
FROM students
GROUP BY 1
ORDER BY 2 DESC;
""".strip()


def build():
    panels = [
        stat_panel(1, "Estudiantes Analizados", SQL_KPI_TOTAL, 0, unit="none", color="blue", decimals=0),
        stat_panel(2, "Nota Final Promedio", SQL_KPI_NOTA, 6, unit="none", color="green"),
        stat_panel(3, "Asistencia Media", SQL_KPI_ASIST, 12, unit="percent", color="purple"),
        stat_panel(4, "Alumnos en Riesgo", SQL_KPI_RIESGO, 18, unit="percent", color="red"),

        line_panel(
            10,
            "P1 · El agotamiento limita el retorno del esfuerzo",
            "Nota final promedio según las horas de estudio semanales, separando a los "
            "alumnos agotados (estrés ≥7 y sueño <6h) del resto. La menor pendiente del "
            "grupo agotado muestra que el desgaste reduce el beneficio de estudiar.",
            SQL_P1, 0, 4, 12, 9,
            xfield="Horas de estudio (semanales)",
            ymin=40, ymax=80, ytitle="Nota Final (0-100)",
            palette={
                "Agotado (estrés alto + poco sueño)": "red",
                "Descansado (resto)": "green",
            },
        ),
        line_panel(
            11,
            "P2 · La brecha digital amplía la diferencia de rendimiento",
            "Nota final promedio según horas de estudio, separando por calidad de la "
            "conexión a internet. Las líneas se abren en abanico: a mejor conectividad, "
            "mayor retorno por cada hora estudiada.",
            SQL_P2, 12, 4, 12, 9,
            xfield="Horas de estudio (semanales)",
            ymin=40, ymax=80, ytitle="Nota Final (0-100)",
            palette={
                "Internet Malo / Crítico (0-4.5)": "red",
                "Internet Regular / Bueno (4.6-7.5)": "orange",
                "Internet Excelente (7.6-10)": "green",
            },
        ),
        bar_panel(
            12,
            "P3 · Qué distingue al éxito autónomo del esfuerzo ansioso",
            "Comparación de hábitos entre el perfil 'Autónomo Exitoso' (baja asistencia, "
            "nota ≥80) y el perfil 'Ansiedad / Esfuerzo Ineficiente' (muchas horas, nota "
            "<60). El primero combina alta motivación y autoeficacia con bajo estrés.",
            SQL_P3, 0, 13, 12, 9,
            orientation="horizontal",
            xfield="Hábito",
            ymin=0, ytitle="Valor promedio",
            palette={
                "Autónomo Exitoso": "green",
                "Ansiedad / Esfuerzo Ineficiente": "red",
            },
        ),
        bar_panel(
            13,
            "Contexto · Porcentaje de alumnos en riesgo por carrera",
            "Proporción de estudiantes marcados con alerta de riesgo académico en cada "
            "carrera. Permite priorizar dónde concentrar las acciones de apoyo.",
            SQL_CARRERA, 12, 13, 12, 9,
            orientation="horizontal",
            xfield="Carrera",
            unit="percent",
            ymin=0,
            ytitle="% en riesgo",
            palette={"% En Riesgo": "orange"},
        ),
    ]

    dashboard = {
        "uid": "tpi-academico",
        "title": "TPI · Desempeño Académico (Hito 3)",
        "description": "Dashboard del Hito 3 que responde las 3 preguntas de investigación "
                       "del Hito 1 sobre riesgo académico, brecha digital y comportamientos atípicos.",
        "tags": ["tpi", "educacion", "hito3"],
        "timezone": "browser",
        "schemaVersion": 39,
        "version": 1,
        "refresh": "",
        "time": {"from": "now-6h", "to": "now"},
        "editable": True,
        "fiscalYearStartMonth": 0,
        "graphTooltip": 0,
        "panels": panels,
        "templating": {"list": []},
        "annotations": {"list": []},
    }
    return dashboard


def main():
    dash = build()
    out1 = os.path.join(BASE_DIR, "grafana", "dashboards", "tpi_dashboard.json")
    out2 = os.path.join(BASE_DIR, "dashboard.json")
    os.makedirs(os.path.dirname(out1), exist_ok=True)
    for path in (out1, out2):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(dash, f, ensure_ascii=False, indent=2)
        print(f"[OK] Escrito: {path}")


if __name__ == "__main__":
    main()
