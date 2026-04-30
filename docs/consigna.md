# Consigna: Trabajo Práctico Integrador (TPI)

## Objetivo General
Desarrollar un sistema de análisis y visualización de datos que permita diagnosticar el desempeño académico, identificar factores de riesgo y proponer soluciones basadas en evidencia. Los estudiantes deberán demostrar sus habilidades de programación para transformar datos crudos en un **Informe de Gestión Interactivo**.

---

## Fases del Proyecto (Hitos)

### Hito 1: Adquisición y Planteo
*   **Dataset:** Selección de un conjunto de datos (mínimo 5000 registros) relacionado con educación (Kaggle, datos abiertos o simulados).
*   **Objetivos:** Definir 3 preguntas de negocio/pedagógicas de alta complejidad (ej: "¿Qué patrones de comportamiento en entregas preceden al abandono del examen parcial?").

### Hito 2: ETL y Calidad de Datos (Exploratory Data Analysis)
Como programadores, se espera un proceso de ETL robusto:
*   **Limpieza:** Tratamiento avanzado de nulos, eliminación de outliers mediante métodos estadísticos y normalización de strings.
*   **Feature Engineering:** Creación de nuevas variables (ej: "Índice de Constancia" basado en fechas de entrega).

### Hito 3: Visualización Dinámica y Análisis
*   **Generación de gráficos:** Mínimo 4 utilizando Matplotlib y Seaborn.
*   **Profesionalismo:** Los gráficos deben incluir títulos, leyendas, escalas correctas y un análisis escrito de qué "dice" el gráfico.

### Hito 4: Interfaz Gráfica (Dashboard Interactivo)
Este es el diferencial técnico. El grupo deberá presentar una interfaz funcional donde el usuario pueda interactuar con los datos.
*   **Opción A (Recomendada):** Uso de **Streamlit** o **Gradio** para crear un dashboard web con Python.
*   **Opción B (Avanzada):** Integración de las visualizaciones en una aplicación de escritorio o web propia.
*   **Requisito:** La interfaz debe permitir filtrar datos (por comisión, estado o fecha) y actualizar los gráficos en tiempo real.

### Hito 5: Informe de Gestión y Propuesta
Basados en la evidencia hallada, redactar un diagnóstico y dos propuestas de mejora académica factibles, justificando por qué esas acciones tendrían impacto según los datos analizados.

---

## Criterios de Evaluación (Rúbrica)

| Criterio | Descripción | Peso |
| :--- | :--- | :--- |
| **Calidad de Código** | Uso de funciones, modularización y manejo de errores (Try-Except). | 20% |
| **Lógica Pandas** | Eficiencia en el filtrado y transformación de grandes volúmenes de datos. | 25% |
| **UX / Dashboard** | Interactividad, facilidad de uso y claridad visual de la interfaz. | 25% |
| **Análisis Crítico** | Capacidad de convertir datos en propuestas de mejora coherentes. | 30% |

---

## Sugerencia
Como programadores, su objetivo no es solo que el código corra, sino que el usuario final (que no sabe programar) entienda la situación de su clase con solo mirar su interfaz. **Piensen en la experiencia de usuario y en la integridad de los datos.**
