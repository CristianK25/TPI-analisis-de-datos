# TPI Análisis de Datos: Desempeño Académico 🎓

Este repositorio contiene el Trabajo Práctico Integrador para la materia **Análisis de Datos Inicial** de la Tecnicatura Universitaria en Programación (TUP).

## 👥 Integrantes

- **Cristian Krahulik**
- **Tomas Mastropietro**
- **Juan Segura**
- **Lautaro Castillo**

---

## 📂 Estructura del Proyecto

El proyecto está organizado siguiendo estándares de ingeniería de datos para asegurar la modularidad y escalabilidad:

- **`data/`**: Carpeta destinada a los datasets (ver sección de _Datos_).
- **`src/`**: Contiene el motor lógico del proyecto (`etl.py`). Aquí se encuentra la inteligencia para auditar y limpiar los datos de forma dinámica.
- **`notebooks/`**: Cuadernos de Jupyter donde se documenta el análisis paso a paso y la narrativa del proyecto.
- **`docs/`**: Consignas y documentación adicional.

---

## 📊 Datos (Datasets)

Debido al volumen de los datos, los archivos CSV se gestionan a través de **GitHub Releases** y **Google Drive**. Puede descargar las versiones necesarias desde:

- 📦 **[GitHub Releases](https://github.com/CristianK25/TPI-analisis-de-datos/releases)**
- ☁️ **[Google Drive](https://drive.google.com/drive/folders/1FkKycqS1PaqQvUDf2MsaTiYRerndTYQ7?usp=sharing)**

Los archivos disponibles son:

1.  **`dataset_ORIGINAL.csv`**: Datos fuente sin procesar.
2.  **`dataset_DIRTY.csv`**: Dataset con ruido inducido (nulos, outliers y duplicados) para validar el proceso de limpieza (**Requerido para el Hito 2**).
3.  **`dataset_CLEAN.csv`**: Dataset purgado y enriquecido con nuevas variables, listo para el análisis estadístico.

---

## ⚙️ Configuración del Entorno

### Con Miniconda (Recomendado)

Si utiliza Miniconda o Anaconda:

```bash
conda create -n tpi-analisis python=3.13
conda activate tpi-analisis
pip install -r requirements.txt
```

### Sin Miniconda (Entorno Virtual)

Si no dispone de Conda, puede utilizar `venv`:

```bash
python -m venv .venv
source .venv/bin/activate  # En Linux/Mac
# .venv\Scripts\activate   # En Windows
pip install -r requirements.txt
```

---

## 🛠️ Herramientas y Scripts

### Proceso ETL (`src/etl.py`)

Hemos desarrollado un motor de ETL robusto que realiza un flujo de **Auditoría -> Limpieza -> Verificación**.

- **`auditar_datos(df)`**: Detecta dinámicamente nulos, duplicados y outliers basados en reglas de negocio.
- **`limpiar_datos(df)`**: Corrige las inconsistencias detectadas (imputación por mediana para números y moda para categorías).
- **`ejecutar_etl()`**: Orquesta el proceso completo de punta a punta.

### Notebook Principal

El archivo `notebooks/TPI_Analisis_Datos.ipynb` es el eje central de la entrega. En él se encuentran:

- **Hito 1**: Planteo de objetivos y 3 preguntas de investigación complejas sobre brecha digital y riesgo académico.
- **Hito 2**: Ejecución y demostración del proceso de limpieza utilizando el motor de `src`.

---

## 🚀 Hoja de Ruta (Roadmap para Hitos 3 y 4)

Este proyecto ha sido entregado con los **Hitos 1 y 2 finalizados y pulidos**. Los siguientes pasos para el equipo son:

1.  **Hito 3 (Análisis Visual)**: Utilizar `dataset_CLEAN.csv` para generar gráficos en el Notebook que respondan a las preguntas planteadas en el Hito 1.
2.  **Hito 4 (Dashboard)**: Desarrollar la interfaz en Streamlit consumiendo el dataset limpio y las funciones de `src`.

---

_Este proyecto utiliza una arquitectura modular. Para cualquier modificación en las reglas de limpieza, por favor edite el diccionario `REGLAS_CALIDAD` en `src/etl.py`._
