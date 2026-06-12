# Hito 3 – Visualización Dinámica con Grafana 📊

Este hito responde **visualmente** las 3 preguntas de investigación del Hito 1
mediante un dashboard de **Grafana** alimentado por una base **PostgreSQL** que
contiene el dataset limpio (`dataset_CLEAN.csv`, 500.000 registros).

Todo corre **localmente con Docker**: no hace falta instalar Grafana ni Postgres
a mano.

---

## 🏗️ Arquitectura

```
 data/dataset_CLEAN.csv
          │  (src/load_db.py – carga por bloques con COPY)
          ▼
 ┌──────────────────┐      ┌──────────────────┐      ┌────────────────────┐
 │   PostgreSQL 16  │◄─────│     Grafana 11   │─────►│  image-renderer    │
 │  tabla students  │ SQL  │  dashboard +     │ PNG  │  (capturas)        │
 │  (500k filas)    │      │  datasource      │      │                    │
 └──────────────────┘      └──────────────────┘      └────────────────────┘
        :5432                    :3000                       :8081
```

Los tres servicios se levantan con un solo `docker compose up -d`. El datasource
y el dashboard se **provisionan automáticamente** desde la carpeta `grafana/`.

---

## ❓ Las 3 preguntas y qué panel las responde

| # | Pregunta de investigación (Hito 1) | Panel del dashboard |
|---|---|---|
| **P1** | ¿En qué medida el **agotamiento** (estrés alto + poco sueño) anula el beneficio del esfuerzo académico? | **P1 · El agotamiento limita el retorno del esfuerzo** — líneas de tendencia OLS de la nota final vs. horas de estudio, separando agotados de descansados. |
| **P2** | ¿Cómo condiciona la **calidad de internet** la efectividad de las horas de estudio? | **P2 · La brecha digital amplía la diferencia de rendimiento** — líneas de tendencia por nivel de conectividad (Malo / Regular / Excelente). |
| **P3** | ¿Qué hábitos distinguen al **éxito por estudio autónomo** del **esfuerzo ansioso e ineficiente**? | **P3 · Qué distingue al éxito autónomo del esfuerzo ansioso** — barras comparando biblioteca, motivación, autoeficacia y estrés entre ambos perfiles. |

Además, el dashboard incluye **4 KPIs** de encabezado (estudiantes, nota
promedio, asistencia media, % en riesgo) y un panel de **contexto** con el % de
alumnos en riesgo por carrera.

### Cómo se construye cada respuesta (metodología)

- **P1 y P2** usan **regresión lineal (OLS)** calculada en SQL con las funciones
  nativas de PostgreSQL `regr_slope()` y `regr_intercept()`. Es la misma técnica
  de "línea de tendencia" del notebook del Hito 1. Se eligió la tendencia en
  lugar del promedio crudo por bin porque el dataset contiene un grupo de
  *outliers inyectados* (el perfil "Ansiedad", con muchas horas y baja nota, que
  se analiza en P3) concentrado por encima de las 30 h; promediar crudo
  deformaría la curva, mientras que la recta de tendencia refleja la relación
  esfuerzo→rendimiento real de cada grupo.
- **P3** segmenta dos perfiles extremos con reglas lógicas:
  - *Autónomo Exitoso*: `attendance_rate < 60` **y** `final_exam_score >= 80`.
  - *Ansiedad / Esfuerzo Ineficiente*: `weekly_study_hours >= 30` **y** `final_exam_score < 60`.

---

## ▶️ Cómo reproducirlo paso a paso

### Requisitos
- **Docker Desktop** instalado y corriendo.
- **Python 3.11+** con las dependencias del repo (`pip install -r requirements.txt`).
- El archivo `data/dataset_CLEAN.csv` (descargable desde el Google Drive del repo,
  ver README). Si no está, `load_db.py` avisa.

### Paso 1 – Levantar el stack
```bash
docker compose up -d
```
Esto descarga (la primera vez) y levanta PostgreSQL, Grafana y el renderer.

### Paso 2 – Cargar el dataset a la base
```bash
python src/load_db.py
```
Carga las 500.000 filas en la tabla `students` (~15 s usando COPY por bloques).

### Paso 3 – Ver el dashboard
Abrí **http://localhost:3000** en el navegador. El acceso es **anónimo** (sin
login). El dashboard está en la carpeta *"TPI - Análisis de Datos"* →
*"TPI · Desempeño Académico (Hito 3)"*.

### Paso 4 – (Opcional) Regenerar las capturas
```bash
python grafana/capturas.py
```
Guarda un PNG por panel + uno del dashboard completo en `docs/capturas/`.

### Apagar todo
```bash
docker compose down          # detiene los contenedores
docker compose down -v       # además borra los datos de Postgres
```

---

## 📁 Archivos de este hito

```
TPI-analisis-de-datos/
├── docker-compose.yml              ← Postgres + Grafana + renderer
├── dashboard.json                  ← ENTREGA: dashboard exportado
├── src/
│   └── load_db.py                  ← Carga el CSV a PostgreSQL (COPY por bloques)
├── grafana/
│   ├── build_dashboard.py          ← Genera dashboard.json (dashboard como código)
│   ├── capturas.py                 ← Exporta los paneles a PNG vía el renderer
│   ├── provisioning/
│   │   ├── datasources/datasource.yml   ← Datasource PostgreSQL (auto)
│   │   └── dashboards/dashboards.yml     ← Provider de dashboards (auto)
│   └── dashboards/
│       └── tpi_dashboard.json      ← Copia que Grafana provisiona al arrancar
└── docs/capturas/                  ← ENTREGA: capturas de cada panel
```

> El dashboard se mantiene **como código** en `grafana/build_dashboard.py`. Para
> modificar un panel se edita ese script y se corre `python grafana/build_dashboard.py`,
> que reescribe `dashboard.json` y la copia provisionada. Grafana recarga los
> cambios solo (cada 10 s).

---

## 🔧 Decisiones técnicas

- **PostgreSQL en vez de SQLite**: Grafana trae el datasource de PostgreSQL de
  fábrica (SQLite requiere un plugin de terceros). Además, PostgreSQL resuelve
  las agregaciones y la regresión OLS (`regr_slope`/`regr_intercept`)
  directamente en la base, sin cálculo en el cliente.
- **Acceso anónimo como Admin**: simplifica la corrección (no hay que loguearse)
  y permite que el `image-renderer` capture los paneles sin credenciales.
- **Carga con `COPY`**: insertar 500k filas con `INSERT` fila a fila sería lento;
  `COPY` por bloques de 50k lo resuelve en segundos.
