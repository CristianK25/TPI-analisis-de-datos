# Hito 4 – Dashboard Interactivo

## ¿Qué es esto?

Es una aplicación web que corre **en tu computadora** (no necesitás internet). La abrís en el navegador y podés explorar los datos del TPI de forma visual: filtrás, hacés clic en los gráficos, y todo se actualiza solo.

La tecnología que usa se llama **Streamlit**: una librería de Python que convierte código Python en una página web interactiva sin necesidad de saber HTML ni JavaScript.

---

## Cómo correrlo

### Paso 1 – Instalar dependencias (solo la primera vez)

Abrí una terminal en la carpeta del proyecto y ejecutá:

```bash
pip install -r requirements.txt
```

Esto instala Streamlit, Plotly, Pandas y todo lo demás que necesita el dashboard.

### Paso 2 – Lanzar el dashboard

```bash
streamlit run app.py
```

Streamlit va a imprimir algo así:

```
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8501
```

Se abre automáticamente en el navegador. Si no se abre solo, copiá esa URL y pegala en Chrome/Firefox.

### Paso 3 – Usarlo

- Los **filtros** están en el panel izquierdo (sidebar).
- Cada vez que cambiás un filtro, **todos los gráficos y métricas se actualizan solos**.
- Para cerrar el dashboard, volvé a la terminal y presioná `Ctrl + C`.

---

## Estructura de archivos

```
TPI-analisis-de-datos/
│
├── app.py               ← Punto de entrada. Solo orquesta, no hace cálculos.
│
├── src/
│   ├── data_loader.py   ← Carga el CSV del dataset limpio
│   ├── filters.py       ← Dibuja el sidebar y filtra los datos
│   ├── kpis.py          ← Muestra las 5 métricas del encabezado
│   ├── graph.py         ← Las 6 funciones que generan los gráficos
│   └── etl.py           ← Pipeline de limpieza (Hitos 1, 2 y 3)
│
├── data/
│   ├── dataset_ORIGINAL.csv
│   ├── dataset_DIRTY.csv
│   └── dataset_CLEAN.csv  ← Este es el que usa el dashboard
│
└── requirements.txt     ← Lista de librerías necesarias
```

---

## Qué hace cada archivo

### `app.py` – El director de orquesta

No hace nada por sí solo. Su único trabajo es:

1. Configurar la página (título, ícono, layout ancho)
2. Llamar a `cargar_datos()` para obtener el DataFrame
3. Llamar a `aplicar_filtros()` para filtrar según lo que eligió el usuario
4. Mostrar una alerta automática si el porcentaje de alumnos en riesgo supera el 10% (amarilla) o el 20% (roja)
5. Llamar a `mostrar_kpis()` para dibujar las métricas
6. Llamar a cada función de `graph.py` y mostrar el gráfico resultante

```python
# Así se ve app.py por dentro (simplificado)
df_full = cargar_datos()          # 1. Cargo datos
df = aplicar_filtros(df_full)     # 2. Filtro según sidebar
mostrar_kpis(df, total=len(df_full))  # 3. Muestro KPIs
st.plotly_chart(grafico_distribucion_notas(df))  # 4. Muestro gráfico
```

---

### `src/data_loader.py` – Carga de datos

Lee el archivo `data/dataset_CLEAN.csv` y lo convierte en un DataFrame de Pandas. Tiene un decorador `@st.cache_data` que hace que el CSV se lea **una sola vez** aunque el usuario cambie filtros cien veces. Sin esto, cada interacción releería 500.000 filas desde disco y sería lentísimo.

```python
@st.cache_data          # ← "guardá el resultado en memoria"
def cargar_datos():
    df = pd.read_csv("data/dataset_CLEAN.csv")
    df["Alerta_Riesgo"] = df["Alerta_Riesgo"].astype(bool)
    return df
```

---

### `src/filters.py` – El sidebar

Dibuja los controles interactivos del panel izquierdo y aplica los filtros sobre el DataFrame completo. Devuelve un DataFrame más chico con solo las filas que cumplen todas las condiciones elegidas.

**Filtros disponibles:**

| Filtro | Tipo de control | Columna del dataset |
|---|---|---|
| Comisión / Semestre | Lista múltiple | `Semester_ID` (1 al 8) |
| Estado de alerta | Botón de opción | `Alerta_Riesgo` (En riesgo / Sin riesgo / Todos) |
| Género | Lista múltiple | `Gender` |
| Carrera | Lista múltiple | `Major_Subject` |
| Rango de edad | Slider | `Age` |

Cuando el usuario selecciona, por ejemplo, solo el Semestre 3 y solo estudiantes en riesgo, `filters.py` devuelve únicamente esas filas. Todos los gráficos y KPIs trabajan sobre ese subconjunto.

---

### `src/kpis.py` – Las 5 métricas del encabezado

Muestra una fila de tarjetas numéricas que resumen el estado de los datos filtrados en ese momento:

| Métrica | Qué muestra |
|---|---|
| Estudiantes | Cantidad de filas que pasaron los filtros |
| Promedio Final | Media de `Final_Exam_Score` |
| Promedio GPA | Media de `Previous_GPA` |
| Asistencia media | Media de `Attendance_Rate` en % |
| En riesgo | Cantidad y % de estudiantes con `Alerta_Riesgo = True` |

El delta del KPI "En riesgo" aparece en **rojo** cuando el porcentaje es alto (usa `delta_color="inverse"` porque más riesgo es peor).

---

### `src/graph.py` – Los 6 gráficos

Cada función recibe el DataFrame ya filtrado y devuelve una figura de Plotly. `app.py` es quien la muestra con `st.plotly_chart()`.

#### 1. `grafico_distribucion_notas(df)`
**Histograma** de `Final_Exam_Score` separado por género (superpuesto con transparencia). Muestra cómo se distribuyen las notas y si hay diferencias entre géneros.

#### 2. `grafico_riesgo_por_carrera(df)`
**Barras horizontales** con el porcentaje de alumnos en riesgo por carrera. El color va de verde (bajo riesgo) a rojo (alto riesgo) usando la escala `RdYlGn_r`.

#### 3. `grafico_estudio_vs_nota(df)`
**Scatter plot** de horas de estudio semanales vs. nota final. Los puntos en riesgo son rojos, los sanos son verdes. Incluye una **línea de tendencia OLS** (regresión lineal) para ver la correlación. Usa una muestra de 3.000 alumnos para no saturar el gráfico.

#### 4. `grafico_evolucion_semestre(df)`
**Gráfico de líneas** con tres métricas promediadas por semestre: Nota Final, Nota del Parcial (eje izquierdo, escala 0–100) y GPA promedio (eje derecho, escala 0–4). Útil para ver si el rendimiento mejora o empeora con los semestres.

#### 5. `grafico_estres_sueno(df)`
**Heatmap de densidad**: cuántos estudiantes hay en cada combinación de horas de sueño + nivel de estrés. Las zonas más oscuras (amarillo en escala Viridis) tienen más concentración de estudiantes.

#### 6. `grafico_top_universidades(df)`
**Barras horizontales** con las 10 universidades con mejor promedio de nota final (solo cuenta universidades con al menos 50 alumnos en el filtro actual para que el promedio sea representativo).

---

## Flujo completo de una interacción

```
Usuario mueve un filtro en el sidebar
         │
         ▼
Streamlit re-ejecuta app.py de arriba a abajo
         │
         ▼
cargar_datos()        → devuelve el DataFrame completo (desde caché, instantáneo)
         │
         ▼
aplicar_filtros()     → devuelve solo las filas que cumplen los filtros
         │
         ▼
mostrar_kpis()        → recalcula y muestra las 5 métricas con los datos nuevos
         │
         ▼
grafico_X(df)  ×6     → recalcula y muestra cada gráfico con los datos nuevos
         │
         ▼
El navegador muestra la página actualizada
```

Todo este ciclo tarda menos de 1 segundo gracias al caché del CSV.

---

## Preguntas frecuentes

**¿Por qué no abre solo en el navegador?**
Copiá `http://localhost:8501` y pegalo manualmente.

**¿Puedo correrlo sin internet?**
Sí, todo corre local. Solo necesitás internet para instalar las dependencias por primera vez (`pip install`).

**¿El dashboard modifica el dataset?**
No. Solo lee `dataset_CLEAN.csv`, nunca lo escribe.

**¿Cómo agrego un gráfico nuevo?**
1. Escribís la función en `src/graph.py`
2. La importás en `app.py`
3. La llamás con `st.plotly_chart(tu_funcion(df))`
